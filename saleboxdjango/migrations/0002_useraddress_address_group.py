# Generated by Django 2.1.4 on 2019-03-20 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='address_group',
            field=models.CharField(default='default', max_length=10),
        ),
    ]
