from datetime import date
from decimal import Decimal as D
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory
from django.forms.formsets import BaseFormSet
from django.forms import Form, ModelForm, ValidationError, widgets
from django.db.transaction import atomic
from django import forms
from systori.lib.fields import LocalizedDecimalField
from systori.lib.accounting.tools import Amount
from ..task.models import Job
from .workflow import Account, credit_jobs, debit_jobs
from .constants import TAX_RATE, BANK_CODE_RANGE
from .models import Entry
from ..document.models import Invoice, DocumentTemplate, DocumentSettings, Letterhead
from ..document.type import invoice as invoice_lib
from .report import prepare_transaction_report


class PaymentForm(Form):
    bank_account = forms.ModelChoiceField(label=_("Bank Account"), queryset=Account.objects.banks())
    amount = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=4)
    transacted_on = forms.DateField(label=_("Received Date"), initial=date.today, localize=True)
    invoice = forms.ModelChoiceField(label=_("Invoice"), queryset=Invoice.objects.all(), widget=forms.HiddenInput(), required=False)
    discount = forms.TypedChoiceField(
            label=_('Is discounted?'), coerce=D,
            choices=[
                ('0.0', _('0%')),
                ('0.03', _('3%')),
                ('0.05', _('5%')),
                ('0.1', _('10%')),
            ]
    )
    is_adjusted = forms.BooleanField(label=_('Apply Adjustment?'), initial=True, required=False)


class SplitPaymentForm(Form):
    job = forms.ModelChoiceField(label=_("Job"), queryset=Job.objects.all(), widget=forms.HiddenInput())
    payment = LocalizedDecimalField(label=_("Amount"), max_digits=14, decimal_places=2, required=False)
    discount = LocalizedDecimalField(label=_("Discount"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())
    adjustment = LocalizedDecimalField(label=_("Adjustment"), max_digits=14, decimal_places=2, required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']

        self.fields['job'].queryset = self.job.project.jobs.all()

        self.balance_amount = self.job.account.balance_amount

        for column_name in ['payment', 'discount', 'adjustment']:
            try:
                column_value = self[column_name].value()
                column_amount_gross = self[column_name].field.to_python(column_value)
                if column_amount_gross is None:
                    column_amount_gross = D('0.00')
            except:
                column_amount_gross = D('0.00')

            setattr(self, column_name+'_amount', Amount.from_gross(column_amount_gross, TAX_RATE))

        self.credit_amount = self.payment_amount + self.discount_amount + self.adjustment_amount


class BaseSplitPaymentFormSet(BaseFormSet):

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop('initial', {})
        self.invoice = initial.get('invoice')
        super().__init__(*args, prefix='split', initial=self.get_initial(kwargs.pop('jobs', [])), **kwargs)
        self.payment_form = PaymentForm(*args, initial=initial, **kwargs)
        self.balance_total = Amount.zero()
        self.payment_total = Amount.zero()
        self.discount_total = Amount.zero()
        self.adjustment_total = Amount.zero()
        self.credit_total = Amount.zero()
        for form in self.forms:
            self.balance_total += form.balance_amount
            self.payment_total += form.payment_amount
            self.discount_total += form.discount_amount
            self.adjustment_total += form.adjustment_amount
            self.credit_total += form.credit_amount

    def get_initial(self, jobs):
        initial = []
        previous_debits = self.invoice.json['debits'] if self.invoice else []
        for job in jobs:
            job_dict = {}
            for debit in previous_debits:
                if debit['job.id'] == job.id:
                    job_dict['payment'] = debit['amount_gross']
                    break
            job_dict['job'] = job
            initial.append(job_dict)
        return initial

    def is_valid(self):
        payment_valid = self.payment_form.is_valid()
        splits_valid = super().is_valid()
        return payment_valid and splits_valid

    def clean(self):
        splits = D(0.0)
        for form in self.forms:
            if form.cleaned_data['payment']:
                splits += form.cleaned_data['payment']
        payment = self.payment_form.cleaned_data.get('amount', D(0.0))
        if splits != payment:
            raise forms.ValidationError(_("The sum of splits must equal the payment amount."))

    def get_splits(self):
        splits = []
        for split in self.forms:
            if split.cleaned_data['payment']:
                job = split.cleaned_data['job']
                payment = split.cleaned_data['payment'] or D(0)
                discount = split.cleaned_data['discount'] or D(0)
                adjustment = split.cleaned_data['adjustment'] or D(0)
                splits.append((job, payment, discount, adjustment))
        return splits

    def save(self):
        credit_jobs(
            self.get_splits(),
            self.payment_form.cleaned_data['amount'],
            self.payment_form.cleaned_data['transacted_on'],
            self.payment_form.cleaned_data['bank_account']
        )
        if self.invoice and not self.invoice.status == Invoice.PAID:
            self.invoice.pay()
            self.invoice.save()

SplitPaymentFormSet = formset_factory(SplitPaymentForm, formset=BaseSplitPaymentFormSet, extra=0)


class InvoiceDocumentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(queryset=Invoice.objects.none(), required=False, widget=forms.HiddenInput())
    doc_template = forms.ModelChoiceField(
            queryset=DocumentTemplate.objects.filter(
                    document_type=DocumentTemplate.INVOICE), required=False)
    add_terms = forms.BooleanField(label=_('Add Terms'), initial=True, required=False)
    is_final = forms.BooleanField(label=_('Is Final Invoice?'), initial=False, required=False)

    title = forms.CharField(label=_('Title'), initial=_("Invoice"))
    header = forms.CharField(widget=forms.Textarea)
    footer = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Invoice
        fields = ['parent', 'doc_template', 'is_final', 'document_date', 'invoice_no', 'title', 'header', 'footer', 'add_terms', 'notes']
        widgets = {
            'document_date': widgets.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].queryset = Invoice.objects.filter(project=self.instance.project)
        if not self.initial.get('header', None) or not self.initial.get('footer', None):
            default_text = DocumentSettings.get_for_language(settings.LANGUAGE_CODE)
            if default_text and default_text.invoice_text:
                rendered = default_text.invoice_text.render(self.instance.project)
                self.initial['header'] = rendered['header']
                self.initial['footer'] = rendered['footer']


class DebitForm(Form):
    """ Represents a debit line for a single job/receivables account on an invoice. """

    is_invoiced = forms.BooleanField(initial=True, required=False)
    job = forms.ModelChoiceField(queryset=Job.objects.none(), widget=forms.HiddenInput())
    amount_net = LocalizedDecimalField(initial=D(0.0), max_digits=14, decimal_places=2, required=False)
    is_override = forms.BooleanField(initial=False, required=False, widget=forms.HiddenInput())
    override_comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.job = self.initial['job']

        self.fields['job'].queryset = self.job.project.jobs.all()
        self.fields['amount_net'].widget.attrs['class'] = 'form-control'
        if str(self['is_invoiced'].value()) == 'False':
            self.fields['amount_net'].widget.attrs['disabled'] = True
        comment_attrs = self.fields['override_comment'].widget.attrs
        comment_attrs['class'] = 'job-override-comment form-control'
        del comment_attrs['cols']
        del comment_attrs['rows']

        self.latest_estimate = Amount.from_net(self.job.estimate_total, TAX_RATE)
        self.latest_itemized = Amount.from_net(self.job.billable_total, TAX_RATE)
        self.latest_percent_complete = self.job.complete_percent

        try:
            amount_net_value = self['amount_net'].value()
            original_debit_amount_net = self['amount_net'].field.to_python(amount_net_value)
            if original_debit_amount_net is None:
                original_debit_amount_net = D('0.00')
        except:
            original_debit_amount_net = D('0.00')

        self.debit_amount = Amount.from_net(original_debit_amount_net, TAX_RATE)

        if self.initial['is_booked']:
            # accounting system already has the 'new' amounts since this invoice was booked
            self.new_debited = self.job.account.debits().sum_amount
            self.new_balance = self.job.account.balance_amount

            # we need to undo the booking to get the 'base' amounts
            self.base_debited = self.new_debited - self.debit_amount
            self.base_balance = self.new_balance - self.debit_amount

        else:
            # no transactions exist yet so the account balance and debits don't include this new debit
            # accounting system has the 'base' amounts
            self.base_debited = self.job.account.debits().sum_amount
            self.base_balance = self.job.account.balance_amount

        # subtract all previous debits from all work completed to get amount not yet debited
        self.billable_amount = self.latest_itemized - self.base_debited

        if str(self['is_override'].value()) == 'False':
            if self.billable_amount.net > 0:
                self.debit_amount = self.billable_amount
                self.initial['amount_net'] = self.debit_amount.net
            else:
                self.debit_amount = Amount.zero()

        # now that we know the correct debit amount we can calculate what the new balance will be
        self.new_debited = self.base_debited + self.debit_amount
        self.new_balance = self.base_balance + self.debit_amount

        self.new_debited_percent = 0
        if self.latest_estimate.net > 0:
            if self.new_debited.net >= self.latest_estimate.net:
                self.new_debited_percent = 100
            else:
                self.new_debited_percent = round((self.new_debited.net / self.latest_estimate.net) * 100, 2)

        if self.initial['is_booked']:
            # previous values come from json, could be different from latest values
            self.previous_debited = Amount.from_gross(D(str(self.initial['debited_gross'])), TAX_RATE)
            self.previous_balance = Amount.from_gross(D(str(self.initial['balance_gross'])), TAX_RATE)
            self.previous_estimate = Amount.from_net(D(str(self.initial['estimate_net'])), TAX_RATE)
            self.previous_itemized = Amount.from_net(D(str(self.initial['itemized_net'])), TAX_RATE)
        else:
            # latest and previous are the same when there is nothing booked yet
            self.previous_debited = self.new_debited
            self.previous_balance = self.new_balance
            self.previous_estimate = self.latest_estimate
            self.previous_itemized = self.latest_itemized

        # used to show user what has changed since last time invoice was created/edited
        self.diff_debited = self.new_debited - self.previous_debited
        self.diff_balance = self.new_balance - self.previous_balance
        self.diff_estimate = self.latest_estimate - self.previous_estimate
        self.diff_itemized = self.latest_itemized - self.previous_itemized
        self.diff_debit_amount = self.debit_amount - Amount.from_net(original_debit_amount_net, TAX_RATE)

    def clean(self):
        if self.cleaned_data['is_override'] and \
                        len(self.cleaned_data['override_comment']) < 2:
            self.add_error('override_comment',
                           ValidationError(_("A comment is required for flat invoice.")))

    def get_initial(self):
        """
        This dictionary later becomes the 'initial' value to this form when
        editing the invoice.
        """
        return {
            'job': self.job,
            'is_invoiced': self.cleaned_data['is_invoiced'],
            'amount_net': self.debit_amount.net,
            'amount_gross': self.debit_amount.gross,
            'amount_tax': self.debit_amount.tax,
            'is_override': self.cleaned_data['is_override'],
            'override_comment': self.cleaned_data['override_comment'],
            'debited_gross': self.new_debited.gross,
            'debited_net': self.new_debited.net,
            'debited_tax': self.new_debited.tax,
            'balance_gross': self.new_balance.gross,
            'balance_net': self.new_balance.net,
            'balance_tax': self.new_balance.tax,
            'estimate_net': self.latest_estimate.net,
            'itemized_net': self.latest_itemized.net,
        }


class BaseInvoiceForm(BaseFormSet):

    def __init__(self, *args, instance, jobs, **kwargs):
        super().__init__(*args, prefix='job', initial=self.get_initial(instance, jobs), **kwargs)
        self.invoice_form = InvoiceDocumentForm(*args, instance=instance, initial=instance.json, **kwargs)
        self.estimate_total = Amount.zero()
        self.itemized_total = Amount.zero()
        self.debit_total = Amount.zero()
        self.debited_total = Amount.zero()
        self.balance_total = Amount.zero()
        for form in self.forms:
            if form['is_invoiced'].value():
                self.estimate_total += form.latest_estimate
                self.itemized_total += form.latest_itemized
                self.debit_total += form.debit_amount
                self.debited_total += form.new_debited
                self.balance_total += form.new_balance

    def is_valid(self):
        invoice_valid = self.invoice_form.is_valid()
        debits_valid = super().is_valid()
        return invoice_valid and debits_valid

    @staticmethod
    def get_initial(invoice, jobs):
        initial = []
        previous_debits = invoice.json['debits']
        for job in jobs:

            job_dict = {
                'is_invoiced': False if previous_debits else True,
                'is_booked': False
            }

            for debit in previous_debits:
                if debit['job.id'] == job.id:
                    job_dict = debit.copy()
                    job_dict['is_booked'] = debit.get('is_booked', True)
                    break

            job_dict['job'] = job

            initial.append(job_dict)
        return initial

    def get_data(self):

        return {
            'debits': self.debits,

            'debit_gross': self.debit_total.gross,
            'debit_net': self.debit_total.net,
            'debit_tax': self.debit_total.tax,

            'debited_gross': self.debited_total.gross,
            'debited_net': self.debited_total.net,
            'debited_tax': self.debited_total.tax,

            'balance_gross': self.balance_total.gross,
            'balance_net': self.balance_total.net,
            'balance_tax': self.balance_total.tax
        }

    @atomic
    def save(self):

        self.debits = []
        for debit_form in self.forms:
            if debit_form.cleaned_data['is_invoiced']:
                self.debits.append(debit_form.get_initial())
        jobs = [d['job'] for d in self.debits]

        invoice = self.invoice_form.instance
        data = self.invoice_form.cleaned_data
        data.update(self.get_data())

        if invoice.transaction:
            invoice.transaction.delete()

        skr03_debits = [(debit['job'], debit['amount_gross'], Entry.FLAT_DEBIT if debit['is_override'] else Entry.WORK_DEBIT) for debit in self.debits]
        invoice.transaction = debit_jobs(skr03_debits, recognize_revenue=data['is_final'])

        invoice.letterhead = Letterhead.objects.first()
        invoice.json = invoice_lib.serialize(invoice, data)
        invoice.save()

        # prepare_transaction_report expects the new transaction and invoice to already be in the database

        invoice.json.update(prepare_transaction_report(jobs))
        invoice.save()


InvoiceForm = formset_factory(DebitForm, formset=BaseInvoiceForm, extra=0)


class AccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['name']


class BankAccountForm(ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name']

    def __init__(self, *args, instance=None, **kwargs):
        if instance is None:  # create form
            banks = Account.objects.banks().order_by('-code')
            if banks.exists():
                next_code = int(banks.first().code) + 1
            else:
                next_code = BANK_CODE_RANGE[0]

            if next_code <= BANK_CODE_RANGE[1]:
                # set initial only if we were able to compute code within range
                kwargs['initial'] = {'code': str(next_code)}

            kwargs['instance'] = Account(account_type=Account.ASSET, asset_type=Account.BANK)
        else:
            kwargs['instance'] = instance

        super(BankAccountForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code']

        if not code.isdigit() or \
                        int(code) < BANK_CODE_RANGE[0] or \
                        int(code) > BANK_CODE_RANGE[1]:
            raise ValidationError(_("Account code must be a number between %(min)s and %(max)s inclusive."),
                                  code='invalid', params={'min': BANK_CODE_RANGE[0], 'max': BANK_CODE_RANGE[1]})

        return code
