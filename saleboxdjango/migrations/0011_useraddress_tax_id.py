# Generated by Django 2.1.4 on 2019-04-07 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0010_callbackstore'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='tax_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]