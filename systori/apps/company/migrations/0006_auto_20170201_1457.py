# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-02-01 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("company", "0005_auto_20170120_0515")]

    operations = [
        migrations.AddField(
            model_name="worker",
            name="can_track_time",
            field=models.BooleanField(
                default=False,
                help_text="allow this worker to start/stop work timer",
                verbose_name="can track time",
            ),
        ),
        migrations.AddField(
            model_name="worker",
            name="is_timetracking_enabled",
            field=models.BooleanField(
                default=True,
                help_text="enable timetracking for this worker",
                verbose_name="timetracking enabled",
            ),
        ),
    ]
