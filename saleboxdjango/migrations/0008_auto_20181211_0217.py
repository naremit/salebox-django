# Generated by Django 2.1.4 on 2018-12-11 02:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0007_auto_20181210_2259'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productratingcache',
            old_name='score',
            new_name='rating',
        ),
        migrations.RenameField(
            model_name='productvariantrating',
            old_name='score',
            new_name='rating',
        ),
    ]