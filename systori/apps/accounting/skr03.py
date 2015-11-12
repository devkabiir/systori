from datetime import date
from .models import *
from .constants import *


# Reading material for double entry accounting:
# http://en.wikipedia.org/wiki/Double-entry_bookkeeping_system
# http://www.find-uk-accountant.co.uk/articles/fua/16
# http://www.accountingcoach.com/accounts-receivable-and-bad-debts-expense/explanation
# http://www.ledger-cli.org/3.0/doc/ledger3.html


def create_chart_of_accounts(self=None):
    if not self: self = type('', (), {})()

    self.promised_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_PROMISED_PAYMENTS_CODE)
    self.partial_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_PARTIAL_PAYMENTS_CODE)
    self.tax_payments = Account.objects.create(account_type=Account.LIABILITY, code=SKR03_TAX_PAYMENTS_CODE)

    self.income = Account.objects.create(account_type=Account.INCOME, code=SKR03_INCOME_CODE)
    self.cash_discount = Account.objects.create(account_type=Account.INCOME, code=SKR03_CASH_DISCOUNT_CODE)

    self.bank = Account.objects.create(account_type=Account.ASSET, code=SKR03_BANK_CODE)


def partial_debit(debits):
    """ Debit the customer account with any new work completed or flat invoice. """

    transaction = Transaction()

    for job, amount, is_flat in debits:

        if not amount:
            continue

        # debit the customer account (asset), this increases their balance
        # (+) "good thing", customer owes us more money
        transaction.debit(job.account, amount,
                          entry_type=Entry.FLAT_DEBIT if is_flat else Entry.WORK_DEBIT,
                          job=job)

        # credit the promised payments account (liability), increasing the liability
        # (+) "bad thing", customer owing us money is a liability
        transaction.credit(Account.objects.get(code=SKR03_PROMISED_PAYMENTS_CODE), amount, job=job)

    transaction.save()

    return transaction


def partial_credit(jobs, payment, transacted_on=None, bank=None):
    """ Applies a payment to a list of customer accounts. Including discounts on a per account basis. """

    assert isinstance(payment, Decimal)
    assert payment == sum([p[1] for p in jobs])

    bank = bank or Account.objects.get(code=SKR03_BANK_CODE)
    transacted_on = transacted_on or date.today()

    transaction = Transaction(transacted_on=transacted_on, transaction_type=Transaction.PAYMENT)

    # debit the bank account (asset)
    # (+) "good thing", money in the bank is always good
    transaction.debit(bank, round(payment, 2))

    for (job, credit, discount) in jobs:

        # extract the income part from the payment (sans tax)
        income = round(credit / (1 + TAX_RATE), 2)

        # credit the customer account (asset), decreasing their balance
        # (-) "bad thing", customer owes us less money
        transaction.credit(job.account, credit, entry_type=Entry.PAYMENT, job=job)

        if not job.project.is_settlement:
            # Accounting prior to final invoice has a bunch more steps involved.

            # debit the promised payments account (liability), decreasing the liability
            # (-) "good thing", customer paying debt reduces liability
            transaction.debit(Account.objects.get(code=SKR03_PROMISED_PAYMENTS_CODE), credit, job=job)

            # credit the partial payments account (liability), increasing the liability
            # (+) "bad thing", we are on the hook to finish and deliver the service or product
            transaction.credit(Account.objects.get(code=SKR03_PARTIAL_PAYMENTS_CODE), income, job=job)

            # credit the tax payments account (liability), increasing the liability
            # (+) "bad thing", tax have to be paid eventually
            transaction.credit(Account.objects.get(code=SKR03_TAX_PAYMENTS_CODE), round(credit - income, 2), job=job)

        if discount > 0:

            # extract the original amount invoiced (sans discount)
            pre_discount_credit = round(credit / (1 - discount), 2)
            discount_amount = round(pre_discount_credit - credit, 2)

            # credit the customer account (asset), decreasing their balance
            # (-) "bad thing", customer owes us less money
            transaction.credit(job.account, discount_amount, entry_type=Entry.DISCOUNT, job=job)

            if job.project.is_settlement:
                # Discount after final invoice has a few more steps involved.

                discount_income = round(discount_amount / (1 + TAX_RATE), 2)
                discount_taxes = round(discount_amount - discount_income, 2)

                # debit the cash discounts account (income), decreasing the income
                # (-) "bad thing", less income :-(
                transaction.debit(Account.objects.get(code=SKR03_CASH_DISCOUNT_CODE), discount_income, job=job)

                # debit the tax payments account (liability), decreasing the liability
                # (-) "good thing", less taxes to pay
                transaction.debit(Account.objects.get(code=SKR03_TAX_PAYMENTS_CODE), discount_taxes, job=job)

            else:
                # Discount prior to final invoice is simpler.

                # debit the promised payments account (liability), decreasing the liability
                # (-) "good thing", customer paying debt reduces liability
                transaction.debit(Account.objects.get(code=SKR03_PROMISED_PAYMENTS_CODE), discount_amount, job=job)

    transaction.save()


def final_debit(job):
    """ Similar to partial_debit but also handles a lot of different accounting situations to prepare
        customer's account for final invoice generation.
    """

    transaction = Transaction()

    unpaid_amount = job.account.balance
    if unpaid_amount > 0:
        # reset balance, we'll add unpaid_amount back into a final debit to customer
        transaction.debit(Account.objects.get(code="1710"), unpaid_amount)
        transaction.credit(job.account, unpaid_amount)

    new_amount = job.new_amount_to_debit
    amount = new_amount + unpaid_amount
    income = round(amount / (1 + TAX_RATE), 2)

    # debit the customer account (asset), this increases their balance
    # (+) "good thing", customer owes us more money
    transaction.debit(job.account, amount)

    # credit the income account (income), this increases the balance
    # (+) "good thing", income is good
    transaction.credit(Account.objects.get(code="8400"), income)

    # credit the tax payments account (liability), increasing the liability
    # (+) "bad thing", will have to be paid in taxes eventually
    transaction.credit(Account.objects.get(code="1776"), amount - income)

    payments = job.account.payments().total

    if payments:
        pre_tax_payments = round(payments * -1 / (1 + TAX_RATE), 2)

        # debit the partial payments account (liability), decreasing the liability
        # (-) "good thing", product or service has been completed and delivered
        transaction.debit(Account.objects.get(code="1718"), pre_tax_payments)

        # credit the income account (income), this increases the balance
        # (+) "good thing", income is good
        transaction.credit(Account.objects.get(code="8400"), pre_tax_payments)

    transaction.save()
