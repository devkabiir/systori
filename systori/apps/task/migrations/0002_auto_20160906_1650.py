# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-06 14:50
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progressreport',
            old_name='access',
            new_name='worker',
        ),
    ]
