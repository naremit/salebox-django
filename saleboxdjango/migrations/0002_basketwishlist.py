# Generated by Django 2.1.4 on 2018-12-07 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('saleboxdjango', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasketWishlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('basket_flag', models.BooleanField(default=True)),
                ('quantity', models.IntegerField(default=1)),
                ('weight', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductVariant')),
            ],
        ),
    ]