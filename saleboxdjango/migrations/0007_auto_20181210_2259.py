# Generated by Django 2.1.4 on 2018-12-10 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0006_auto_20181209_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariantrating',
            name='score',
            field=models.IntegerField(default=50),
        ),
    ]
