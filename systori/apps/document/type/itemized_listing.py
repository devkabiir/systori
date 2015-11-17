from io import BytesIO
from datetime import date
from decimal import Decimal

from reportlab.lib.units import mm
from reportlab.lib.pagesizes import landscape
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer

from django.utils.formats import date_format
from django.utils.translation import ugettext as _

from systori.apps.accounting.constants import TAX_RATE
from systori.lib.templatetags.customformatting import money

from .style import SystoriDocument, stylesheet, TableFormatter, ContinuationTable
from .style import LetterheadCanvasWithoutFirstPage
from .style import DOCUMENT_FORMAT, DOCUMENT_UNIT
from .invoice import collate_tasks, collate_tasks_total, serialize

from systori.apps.document.models import DocumentSettings

from . import font

DEBUG_DOCUMENT = False  # Shows boxes in rendered output

def collate_payments(invoice, available_width):

    t = TableFormatter([0, 1, 1, 1], available_width, debug=DEBUG_DOCUMENT)
    t.style.append(('ALIGNMENT', (0, 0), (0, -1), "LEFT"))
    t.style.append(('ALIGNMENT', (1, 0), (-1, -1), "RIGHT"))
    t.style.append(('VALIGN', (0, 0), (-1, -1), "BOTTOM"))
    t.style.append(('RIGHTPADDING', (3, 0), (3, -1), 0))

    t.style.append(('LINEBELOW', (0, 0), (-1, 0), 0.25, colors.black))
    t.style.append(('LINEAFTER', (0, 0), (-2, -1), 0.25, colors.black))


    t.row('', _("gross pay"), _("consideration"), _("VAT"))
    t.row_style('FONTNAME', 0, -1, font.bold)

    if len(invoice['transactions']) > 0:
        t.row(_("Job Performance"), money(invoice['total_gross']), money(invoice['total_base']), money(invoice['total_tax']))

    billable_amount = invoice['total_gross']

    for payment in invoice['transactions']:
        row = ['', money(payment['amount']), money(payment['amount_base']), money(payment['amount_tax'])]
        if payment['type'] == 'payment':
            received_on = date_format(payment['transacted_on'], use_l10n=True)
            row[0] = Paragraph(_('Your Payment on')+' '+received_on, stylesheet['Normal'])
        elif payment['type'] == 'discount':
            row[0] = _('Discount Applied')
        billable_amount += payment['amount']
        t.row(*row)

    t.row(_("Billable Total"), money(billable_amount), money(billable_amount/(TAX_RATE+Decimal('1'))), money(billable_amount/(TAX_RATE+Decimal('1'))*TAX_RATE))

    t.row_style('FONTNAME', 0, -1, font.bold)

    return t.get_table(ContinuationTable, repeatRows=1)


def render(project, format):

    letterhead = DocumentSettings.objects.first().itemized_letterhead

    def canvas_maker(*args, **kwargs):
        return LetterheadCanvasWithoutFirstPage(letterhead.letterhead_pdf, *args, **kwargs)

    with BytesIO() as buffer:
        document_unit = DOCUMENT_UNIT[letterhead.document_unit]
        if letterhead.orientation == 'landscape':
            pagesize = landscape(DOCUMENT_FORMAT[letterhead.document_format])
        else:
            pagesize = DOCUMENT_FORMAT[letterhead.document_format]
        page_width = pagesize[0]
        table_width = page_width - float(letterhead.right_margin)*document_unit\
                                 - float(letterhead.left_margin)*document_unit

        today = date_format(date.today(), use_l10n=True)

        itemized_listing = serialize(project, {})

        doc = SystoriDocument(buffer, pagesize=pagesize, debug=DEBUG_DOCUMENT)

        flowables = [

            Paragraph(_("Itemized listing {}").format(date.today), stylesheet['h2']),

            Paragraph(_("Project") + ": {}".format(project.name), stylesheet['Normal']),
            Paragraph(_("Date") + ": {}".format(today), stylesheet['Normal']),

            Spacer(0, 10*mm),

            collate_payments(itemized_listing, table_width),

            Spacer(0, 10*mm),

            collate_tasks(itemized_listing, table_width),

            Spacer(0, 4*mm),

            collate_tasks_total(itemized_listing, table_width),
            ]

        if format == 'print':
            doc.build(flowables, letterhead=letterhead)
        else:
            doc.build(flowables, letterhead=letterhead, canvasmaker=canvas_maker)


        return buffer.getvalue()
