# Generated by Django 2.1.8 on 2019-12-16 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0014_auto_20191216_1334'),
    ]

    operations = [
        migrations.AddField(
            model_name='analytic',
            name='ip_city',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='ip_country',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='ip_lat',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='ip_lng',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='ip_tz',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
