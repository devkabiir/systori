# Generated by Django 2.0.7 on 2018-08-06 12:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('company', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='project.Project'),
        ),
        migrations.AddField(
            model_name='note',
            name='worker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='notes', to='company.Worker'),
        ),
    ]
