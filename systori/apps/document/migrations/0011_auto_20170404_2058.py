from django.db import migrations
from postgres_schema.operations import RunInSchemas


def migrate_json(apps, schema_editor):
    from systori.apps.document.models import Invoice, Proposal

    for invoice in Invoice.objects.all():
        invoice.json["vesting_start"] = None
        invoice.json["vesting_end"] = None
        invoice.json["project_id"] = invoice.project_id
        invoice.json["show_project_id"] = False
        invoice.save()
    for proposal in Proposal.objects.all():
        proposal.json["project_id"] = proposal.project_id
        proposal.json["show_project_id"] = False


class Migration(migrations.Migration):

    dependencies = [("document", "0010_auto_20170214_0028")]

    operations = [RunInSchemas(migrations.RunPython(migrate_json))]
