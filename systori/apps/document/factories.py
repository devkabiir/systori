import os.path
import factory
from factory import fuzzy
from django.conf import settings

from systori.lib.accounting.tools import Amount

from .models import Proposal, Invoice
from .models import Letterhead, DocumentSettings, DocumentTemplate


class DocumentTemplateFactory(factory.django.DjangoModelFactory):

    name = fuzzy.FuzzyText(length=15)

    class Meta:
        model = DocumentTemplate


class ProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Proposal


class InvoiceFactory(factory.django.DjangoModelFactory):

    json = {"debit": Amount.zero()}

    class Meta:
        model = Invoice


class DocumentSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DocumentSettings


class LetterheadFactory(factory.django.DjangoModelFactory):

    name = fuzzy.FuzzyText(length=15)
    letterhead_pdf = os.path.join(
        settings.BASE_DIR, "apps/document/test_data/letterhead.pdf"
    )

    class Meta:
        model = Letterhead

    @factory.post_generation
    def with_settings(self: Letterhead, create, extracted, **kwargs):
        if create and extracted:
            DocumentSettingsFactory(
                language="de",
                evidence_letterhead=self,
                proposal_letterhead=self,
                invoice_letterhead=self,
                timesheet_letterhead=self,
            )
