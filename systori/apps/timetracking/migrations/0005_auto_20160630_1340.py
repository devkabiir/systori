# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-30 06:39
from __future__ import unicode_literals

from django.db import migrations


def set_date(apps, schema_editor):
    from systori.apps.company.models import Company

    Timer = apps.get_model("timetracking", "Timer")
    for company in Company.objects.all():
        company.activate()
        for timer in Timer.objects.all():
            timer.date = timer.start
            timer.save()


class Migration(migrations.Migration):

    dependencies = [("timetracking", "0004_auto_20160630_1339")]

    operations = [
        migrations.RunPython(set_date, reverse_code=migrations.RunPython.noop)
    ]
