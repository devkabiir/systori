# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-06 03:53
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion
from postgres_schema.operations import RunInSchemas


def upgrade_taskinstance_to_task(apps, schema_editor):
    Job = apps.get_model("task", "Job")
    TOKEN = 11000

    for job in Job.objects.all():

        variant_group = 100

        for task in job.all_tasks.all():

            order_max = None

            is_variant_mode = task.taskinstances.count() > 1
            if is_variant_mode:
                # if variant_group == 100:
                #    print('Project {}: {}, Job {}: {}'.format(
                #        task.job.project.id, task.job.project.name,
                #        task.job.pk, task.job.root.name)
                #    )
                # print('  Variations for {}: {}'.format(task.id, task.name))
                variant_group += 1
                task.variant_group = variant_group
                task.save()

            for taskinstance in task.taskinstances.order_by("-selected"):

                if not taskinstance.selected and not is_variant_mode:
                    raise AssertionError(
                        "If only one task instance it must be selected."
                    )

                if not taskinstance.selected:
                    if order_max is None:
                        order_max = task.group.tasks.aggregate(models.Max("order")).get(
                            "order__max"
                        )
                    order_max += 1
                    TOKEN += 1
                    task.id = None
                    task.token = TOKEN
                    task.order = order_max
                    task.variant_serial += 1
                    task.save()
                    # print("    Variant: {}.{}".format(task.variant_group, task.variant_serial))
                elif is_variant_mode:
                    pass
                    # print("    Primary: {}.{}".format(task.variant_group, task.variant_serial))

                task.qty_equation = str(task.qty)
                task.price = Decimal("0.00")
                # if is_variant_mode: print("    Line items ", end='')
                lineitem_order = 0
                for lineitem in taskinstance.lineitems.all():
                    TOKEN += 1
                    lineitem_order += 1
                    lineitem.token = TOKEN
                    lineitem.order = lineitem_order
                    lineitem.qty_equation = str(lineitem.qty)
                    lineitem.price_equation = str(lineitem.price)
                    lineitem.total = round(lineitem.qty * lineitem.price, 2)
                    task.price += lineitem.total
                    lineitem.task = task
                    lineitem.job = task.job
                    lineitem.save()
                    # if is_variant_mode: print(".", end='')
                # if is_variant_mode: print("")
                task.total = round(task.qty * task.price, 2)
                task.save()

    for job in Job.objects.all():
        for group in job.root.groups.all():
            task_order = 0
            for task in group.tasks.all():
                task_order += 1
                task.order = task_order
                task.save()


def remove_old_content_types(apps, schema_editor):
    from django.contrib.contenttypes.models import ContentType

    ContentType.objects.filter(app_label="task", model="taskgroup").delete()
    ContentType.objects.filter(app_label="task", model="taskinstance").delete()


class Migration(migrations.Migration):

    dependencies = [("task", "0004_data_migration")]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="job",
            field=models.ForeignKey(
                "task.Job", models.CASCADE, related_name="all_tasks"
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="group",
            field=models.ForeignKey("task.Group", models.CASCADE, related_name="tasks"),
        ),
        migrations.RemoveField(model_name="task", name="taskgroup"),
        migrations.DeleteModel("taskgroup"),
        migrations.DeleteModel("oldjob"),
        migrations.AddField(
            model_name="task",
            name="token",
            field=models.BigIntegerField(verbose_name="api token", null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="price",
            field=models.DecimalField(
                decimal_places=4, default=0.0, max_digits=14, verbose_name="Price"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="total",
            field=models.DecimalField(
                decimal_places=4, default=0.0, max_digits=14, verbose_name="Total"
            ),
        ),
        migrations.RenameField(
            model_name="task", old_name="is_optional", new_name="is_provisional"
        ),
        migrations.AddField(
            model_name="task",
            name="variant_group",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name="task",
            name="variant_serial",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="task",
            name="qty_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lineitem",
            name="token",
            field=models.BigIntegerField(verbose_name="api token", null=True),
        ),
        migrations.AddField(
            model_name="lineitem",
            name="is_hidden",
            field=models.BooleanField(default=False),
        ),
        migrations.RenameField(
            model_name="lineitem", old_name="unit_qty", new_name="qty"
        ),
        migrations.AddField(
            model_name="lineitem",
            name="total",
            field=models.DecimalField(
                decimal_places=4, default=0.0, max_digits=14, verbose_name="Total"
            ),
        ),
        migrations.RemoveField(model_name="lineitem", name="task_qty"),
        migrations.AddField(
            model_name="lineitem",
            name="order",
            field=models.PositiveIntegerField(db_index=True, default=1, editable=False),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name="lineitem",
            options={
                "ordering": ("order",),
                "verbose_name": "Line Item",
                "verbose_name_plural": "Line Items",
            },
        ),
        # Add task to lineitem, allowing NULLs
        migrations.AddField(
            model_name="lineitem",
            name="task",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lineitems",
                to="task.Task",
            ),
        ),
        migrations.AddField(
            model_name="lineitem",
            name="job",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="all_lineitems",
                to="task.Job",
            ),
        ),
        migrations.AddField(
            model_name="lineitem",
            name="price_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lineitem",
            name="qty_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="lineitem",
            name="total_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        # properly set all of the jobs
        migrations.RunSQL(
            "SET CONSTRAINTS ALL IMMEDIATE", reverse_sql=migrations.RunSQL.noop
        ),
        RunInSchemas(migrations.RunPython(upgrade_taskinstance_to_task)),
        # Now alter making it NOT NULL
        migrations.AlterField(
            model_name="lineitem",
            name="task",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lineitems",
                to="task.Task",
            ),
        ),
        migrations.AlterField(
            model_name="lineitem",
            name="job",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="all_lineitems",
                to="task.Job",
            ),
        ),
        # Cleanup...
        migrations.RemoveField("lineitem", "taskinstance"),
        migrations.DeleteModel("taskinstance"),
        migrations.RunPython(remove_old_content_types),
        migrations.RemoveField(model_name="lineitem", name="billable"),
        migrations.RemoveField(model_name="lineitem", name="is_labor"),
        migrations.RemoveField(model_name="lineitem", name="is_material"),
        migrations.AddField(
            model_name="lineitem",
            name="complete",
            field=models.DecimalField(
                decimal_places=4, default=0.0, max_digits=14, verbose_name="Completed"
            ),
        ),
        migrations.AddField(
            model_name="task",
            name="total_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lineitem",
            name="unit",
            field=models.CharField(blank=True, max_length=512, verbose_name="Unit"),
        ),
        migrations.AlterField(
            model_name="task",
            name="complete",
            field=models.DecimalField(
                decimal_places=4, default=0.0, max_digits=14, verbose_name="Completed"
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="unit",
            field=models.CharField(blank=True, max_length=512, verbose_name="Unit"),
        ),
        migrations.AddField(
            model_name="task",
            name="price_equation",
            field=models.CharField(blank=True, default="", max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="lineitem",
            name="name",
            field=models.CharField(blank=True, max_length=512, verbose_name="Name"),
        ),
        migrations.AlterField(
            model_name="task", name="description", field=models.TextField(blank=True)
        ),
    ]
