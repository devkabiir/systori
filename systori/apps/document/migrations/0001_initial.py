# Generated by Django 2.1.8 on 2019-07-30 15:31

import datetime
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Adjustment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Adjustment',
                'verbose_name_plural': 'Adjustment',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ('current__uploaded',),
            },
        ),
        migrations.CreateModel(
            name='DocumentSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(choices=[('de', 'Deutsch'), ('en', 'English')], default='de', max_length=2, unique=True, verbose_name='language')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('header', models.TextField(verbose_name='Header')),
                ('footer', models.TextField(verbose_name='Footer')),
                ('document_type', models.CharField(choices=[('proposal', 'Proposal'), ('invoice', 'Invoice')], default='proposal', max_length=128, verbose_name='Document Type')),
            ],
            options={
                'verbose_name': 'Document Template',
                'verbose_name_plural': 'Document Templates',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(max_length=512, upload_to='attachments', verbose_name='File')),
                ('uploaded', models.DateTimeField(auto_now_add=True, verbose_name='Created')),
            ],
            options={
                'ordering': ('uploaded',),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('invoice_no', models.CharField(max_length=30, unique=True, verbose_name='Invoice No.')),
                ('status', django_fsm.FSMField(choices=[('draft', 'Draft'), ('sent', 'Sent'), ('paid', 'Paid')], default='draft', max_length=50)),
            ],
            options={
                'verbose_name': 'Invoice',
                'verbose_name_plural': 'Invoices',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Letterhead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=512, verbose_name='Name')),
                ('letterhead_pdf', models.FileField(upload_to='letterhead', verbose_name='Letterhead PDF')),
                ('document_unit', models.CharField(choices=[('mm', 'mm'), ('cm', 'cm'), ('inch', 'inch')], default='mm', max_length=5, verbose_name='Document Unit')),
                ('top_margin', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Top Margin')),
                ('right_margin', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Right Margin')),
                ('bottom_margin', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Bottom Margin')),
                ('left_margin', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Left Margin')),
                ('top_margin_next', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Top Margin Next')),
                ('bottom_margin_next', models.DecimalField(decimal_places=2, default=Decimal('25'), max_digits=5, verbose_name='Bottom Margin Next')),
                ('document_format', models.CharField(choices=[('A5', 'A5'), ('A4', 'A4'), ('A3', 'A3'), ('LETTER', 'LETTER'), ('LEGAL', 'LEGAL'), ('ELEVENSEVENTEEN', 'ELEVENSEVENTEEN'), ('B5', 'B5'), ('B4', 'B4')], default='A4', max_length=30, verbose_name='Pagesize')),
                ('orientation', models.CharField(choices=[('portrait', 'Portrait'), ('landscape', 'Landscape')], default='portrait', max_length=15, verbose_name='Orientation')),
                ('debug', models.BooleanField(default=True, verbose_name='Debug Mode')),
                ('font', models.CharField(choices=[('OpenSans', 'OpenSans'), ('DroidSerif', 'DroidSerif'), ('Tinos', 'Tinos'), ('Ubuntu', 'Ubuntu')], default='OpenSans', max_length=15, verbose_name='Font')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['document_date'],
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('sent', 'Sent'), ('approved', 'Approved'), ('declined', 'Declined')], default='new', max_length=50)),
            ],
            options={
                'verbose_name': 'Proposal',
                'verbose_name_plural': 'Proposals',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('letterhead', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='refund_documents', to='document.Letterhead')),
            ],
            options={
                'verbose_name': 'Refund',
                'verbose_name_plural': 'Refunds',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Timesheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('json', jsonfield.fields.JSONField(default={})),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('document_date', models.DateField(blank=True, default=datetime.date.today, verbose_name='Date')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Notes')),
                ('letterhead', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='timesheet_documents', to='document.Letterhead')),
                ('worker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timesheets', to='company.Worker')),
            ],
            options={
                'verbose_name': 'Timesheet',
                'verbose_name_plural': 'Timesheets',
                'ordering': ['id'],
                'abstract': False,
            },
        ),
    ]
