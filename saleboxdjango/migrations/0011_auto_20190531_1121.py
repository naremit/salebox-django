# Generated by Django 2.1.8 on 2019-05-31 04:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0010_auto_20190531_1119'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariant',
            old_name='stock_count_total',
            new_name='stock_total',
        ),
    ]