# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-20 14:43
from django.db import migrations, models
import django.db.models.deletion
from systori.apps.project.gaeb import GAEBStructureField


def zfill_field_renamed(apps, schema_editor):
    from systori.apps.company.models import Company
    Project = apps.get_model("project", "Project")
    for company in Company.objects.all():
        company.activate()
        for project in Project.objects.all():
            project.structure = "{}.{}.{}".format(
                '1'.zfill(project.job_zfill),
                '1'.zfill(project.taskgroup_zfill),
                '1'.zfill(project.task_zfill)
            )
            project._meta.local_concrete_fields = project._meta.local_concrete_fields[:-1]
            project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_jobsite_travel_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='structure',
            field=GAEBStructureField(default='01.01.001', verbose_name='Numbering Structure'),
        ),
        migrations.AddField(
            model_name='project',
            name='structure_depth',
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.RunPython(zfill_field_renamed),
        migrations.RemoveField(
            model_name='project',
            name='job_zfill',
        ),
        migrations.RemoveField(
            model_name='project',
            name='taskgroup_zfill',
        ),
        migrations.RemoveField(
            model_name='project',
            name='task_zfill',
        ),
        migrations.AlterModelOptions(
            name='teammember',
            options={'ordering': ['-is_foreman', 'worker__user__first_name']},
        ),
        migrations.RenameField(
            model_name='dailyplan',
            old_name='accesses',
            new_name='workers',
        ),
        migrations.RenameField(
            model_name='teammember',
            old_name='access',
            new_name='worker',
        ),
        migrations.AlterField(
            model_name='teammember',
            name='dailyplan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='project.DailyPlan'),
        ),
    ]
