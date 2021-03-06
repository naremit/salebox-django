# Generated by Django 2.1.8 on 2019-08-29 07:07

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0003_auto_20190827_0809'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='salebox_transactionhistory_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='member',
            name='salebox_transactionhistory_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='member',
            name='salebox_transactionhistory_request_dt',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
    ]
