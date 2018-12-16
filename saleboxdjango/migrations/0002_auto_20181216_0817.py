# Generated by Django 2.1.4 on 2018-12-16 08:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('saleboxdjango', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productvariantrating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='productvariantrating',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductVariant'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='attribute_1',
            field=models.ManyToManyField(related_name='variant_attr_1', to='saleboxdjango.AttributeItem'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='attribute_2',
            field=models.ManyToManyField(related_name='variant_attr_2', to='saleboxdjango.AttributeItem'),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Product'),
        ),
        migrations.AddField(
            model_name='productratingcache',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Product'),
        ),
        migrations.AddField(
            model_name='productcategory',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='saleboxdjango.ProductCategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='attribute_1',
            field=models.ManyToManyField(related_name='product_attr_1', to='saleboxdjango.AttributeItem'),
        ),
        migrations.AddField(
            model_name='product',
            name='attribute_2',
            field=models.ManyToManyField(related_name='product_attr_2', to='saleboxdjango.AttributeItem'),
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductCategory'),
        ),
        migrations.AddField(
            model_name='member',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Country'),
        ),
        migrations.AddField(
            model_name='member',
            name='country_state',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.CountryState'),
        ),
        migrations.AddField(
            model_name='member',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.MemberGroup'),
        ),
        migrations.AddField(
            model_name='member',
            name='group_when_created',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_when_created', to='saleboxdjango.MemberGroup'),
        ),
        migrations.AddField(
            model_name='member',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Member'),
        ),
        migrations.AddField(
            model_name='emailvalidator',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='discountruleset',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.DiscountGroup'),
        ),
        migrations.AddField(
            model_name='discountruleset',
            name='product_variant',
            field=models.ManyToManyField(blank=True, to='saleboxdjango.ProductVariant'),
        ),
        migrations.AddField(
            model_name='countrystate',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Country'),
        ),
        migrations.AddField(
            model_name='basketwishlist',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='basketwishlist',
            name='variant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.ProductVariant'),
        ),
        migrations.AddField(
            model_name='attributeitem',
            name='attribute',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxdjango.Attribute'),
        ),
    ]