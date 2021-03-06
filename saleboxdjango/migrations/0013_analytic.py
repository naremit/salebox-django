# Generated by Django 2.1.8 on 2019-12-16 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0012_auto_20191113_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analytic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(db_index=True, editable=False)),
                ('first_seen', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('page_views', models.IntegerField(default=1)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('ua_browser_family', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_browser_version', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_os_family', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_os_version', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_device_family', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_device_brand', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_device_model', models.CharField(blank=True, max_length=20, null=True)),
                ('ua_is_mobile', models.BooleanField(null=True)),
                ('ua_is_tablet', models.BooleanField(null=True)),
                ('ua_is_touch_capable', models.BooleanField(null=True)),
                ('ua_is_pc', models.BooleanField(null=True)),
                ('ua_is_bot', models.BooleanField(null=True)),
            ],
        ),
    ]
