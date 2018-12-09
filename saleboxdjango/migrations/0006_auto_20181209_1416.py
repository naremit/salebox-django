# Generated by Django 2.1.4 on 2018-12-09 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0005_productvariantrating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productvariantrating',
            name='product',
        ),
        migrations.AddField(
            model_name='productvariantrating',
            name='variant',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductVariant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='productratingcache',
            name='score',
            field=models.IntegerField(default=50),
        ),
        migrations.AlterField(
            model_name='productratingcache',
            name='vote_count',
            field=models.IntegerField(default=1),
        ),
    ]
