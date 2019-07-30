# Generated by Django 2.1.8 on 2019-07-30 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='worker',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='access', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='contract',
            name='worker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contracts', to='company.Worker'),
        ),
        migrations.AddField(
            model_name='company',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='companies', through='company.Worker', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='worker',
            unique_together={('company', 'user')},
        ),
    ]
