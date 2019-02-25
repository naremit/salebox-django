# Generated by Django 2.1.4 on 2019-02-25 04:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductVariantImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.CharField(max_length=100)),
                ('img_height', models.IntegerField()),
                ('img_width', models.IntegerField()),
                ('title', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductVariant')),
            ],
            options={
                'ordering': ('order',),
            },
        ),
    ]