# Generated by Django 2.1.4 on 2019-03-27 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0004_auto_20190327_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkoutstore',
            name='user',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
