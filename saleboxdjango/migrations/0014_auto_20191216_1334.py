# Generated by Django 2.1.8 on 2019-12-16 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0013_analytic'),
    ]

    operations = [
        migrations.AddField(
            model_name='analytic',
            name='language',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='screen_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='analytic',
            name='screen_width',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_browser_family',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Browser family'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_browser_version',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Browser version'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_device_brand',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Device brand'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_device_family',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Device family'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_device_model',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Device model'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_is_bot',
            field=models.BooleanField(null=True, verbose_name='Is bot?'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_is_mobile',
            field=models.BooleanField(null=True, verbose_name='Is mobile?'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_is_pc',
            field=models.BooleanField(null=True, verbose_name='Is PC?'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_is_tablet',
            field=models.BooleanField(null=True, verbose_name='Is tablet?'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_is_touch_capable',
            field=models.BooleanField(null=True, verbose_name='Is touchscreen?'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_os_family',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='OS family'),
        ),
        migrations.AlterField(
            model_name='analytic',
            name='ua_os_version',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='OS version'),
        ),
    ]
