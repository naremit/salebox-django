# Generated by Django 2.1.4 on 2019-04-06 05:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0008_auto_20190406_1159'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkoutstore',
            name='gateway_code',
            field=models.CharField(default='default', max_length=12),
            preserve_default=False,
        ),
    ]