# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-01-20 04:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("company", "0004_worker")]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="is_active",
            field=models.BooleanField(
                default=True, help_text="Use this instead of deleting schema."
            ),
        )
    ]
