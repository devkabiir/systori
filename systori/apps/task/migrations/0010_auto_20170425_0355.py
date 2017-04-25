# Generated by Django 2.0 on 2017-04-25 01:55

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0009_auto_20170314_0157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expendreport',
            name='expended',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Expended'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='expended',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Expended'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='qty',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='lineitem',
            name='total',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='progressreport',
            name='complete',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Complete'),
        ),
        migrations.AlterField(
            model_name='task',
            name='complete',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Completed'),
        ),
        migrations.AlterField(
            model_name='task',
            name='price',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Price'),
        ),
        migrations.AlterField(
            model_name='task',
            name='qty',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=12, null=True, verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='task',
            name='total',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=12, verbose_name='Total'),
        ),
    ]
