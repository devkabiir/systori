# Generated by Django 2.1.8 on 2019-07-30 15:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('document', '0001_initial'),
        ('company', '0001_initial'),
        ('project', '0002_auto_20190730_1731'),
        ('accounting', '0002_auto_20190730_1731'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='refund',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='refunds', to='project.Project'),
        ),
        migrations.AddField(
            model_name='refund',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='refund', to='accounting.Transaction'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='jobs',
            field=models.ManyToManyField(related_name='proposals', to='task.Job', verbose_name='Jobs'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='letterhead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='proposal_documents', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='proposal',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='project.Project'),
        ),
        migrations.AddField(
            model_name='payment',
            name='invoice',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to='document.Invoice'),
        ),
        migrations.AddField(
            model_name='payment',
            name='letterhead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_documents', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='payment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='project.Project'),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to='accounting.Transaction'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='letterhead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_documents', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='document.Invoice'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='project.Project'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoice', to='accounting.Transaction'),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='attachment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='document.Attachment'),
        ),
        migrations.AddField(
            model_name='fileattachment',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='company.Worker'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='evidence_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='invoice_text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.DocumentTemplate'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='itemized_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='proposal_text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.DocumentTemplate'),
        ),
        migrations.AddField(
            model_name='documentsettings',
            name='timesheet_letterhead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='current',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='document.FileAttachment'),
        ),
        migrations.AddField(
            model_name='attachment',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='project.Project'),
        ),
        migrations.AddField(
            model_name='adjustment',
            name='invoice',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adjustment', to='document.Invoice'),
        ),
        migrations.AddField(
            model_name='adjustment',
            name='letterhead',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='adjustment_documents', to='document.Letterhead'),
        ),
        migrations.AddField(
            model_name='adjustment',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjustments', to='project.Project'),
        ),
        migrations.AddField(
            model_name='adjustment',
            name='transaction',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adjustment', to='accounting.Transaction'),
        ),
    ]
