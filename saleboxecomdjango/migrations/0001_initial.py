# Generated by Django 2.1.4 on 2018-12-05 07:09

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Product Attribute',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='AttributeItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.Attribute')),
            ],
            options={
                'verbose_name': 'Product Attribute Item',
                'ordering': ['value'],
            },
        ),
        migrations.CreateModel(
            name='DiscountGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('group_type', models.CharField(choices=[('S', 'Seasonal'), ('M', 'Manual')], default='M', max_length=1)),
                ('operational_flag', models.BooleanField(default=False)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Discount Group',
            },
        ),
        migrations.CreateModel(
            name='DiscountRuleset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('discount_type', models.CharField(choices=[('flat_percent', 'Flat Percentage')], default='flat_percent', max_length=12)),
                ('value', models.IntegerField(blank=True, null=True)),
                ('start_dt', models.DateTimeField(blank=True, null=True)),
                ('end_dt', models.DateTimeField(blank=True, null=True)),
                ('operational_flag', models.BooleanField(default=True)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.DiscountGroup')),
            ],
            options={
                'verbose_name': 'Discount Ruleset',
            },
        ),
        migrations.CreateModel(
            name='LastUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=36)),
                ('value', models.FloatField(default=0.0)),
            ],
            options={
                'verbose_name': 'Last Update',
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.CharField(db_index=True, max_length=25)),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unspecified')], max_length=1, null=True)),
                ('title', models.IntegerField(blank=True, choices=[(1, 'Mr'), (2, 'Mrs'), (3, 'Miss')], null=True)),
                ('name_first', models.CharField(blank=True, max_length=20, null=True)),
                ('name_last', models.CharField(blank=True, max_length=30, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address_1', models.CharField(blank=True, max_length=255, null=True)),
                ('address_2', models.CharField(blank=True, max_length=255, null=True)),
                ('address_3', models.CharField(blank=True, max_length=255, null=True)),
                ('address_4', models.CharField(blank=True, max_length=255, null=True)),
                ('address_5', models.CharField(blank=True, max_length=255, null=True)),
                ('postcode', models.CharField(blank=True, max_length=12, null=True)),
                ('phone_1', models.CharField(blank=True, max_length=20, null=True)),
                ('phone_2', models.CharField(blank=True, max_length=20, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('id_card', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(choices=[('A', 'Active'), ('R', 'Resigned'), ('S', 'Suspended'), ('T', 'Terminated')], default='A', max_length=1)),
                ('active_flag', models.BooleanField(default=True)),
                ('join_date', models.DateField(blank=True, null=True)),
                ('string_1', models.CharField(blank=True, max_length=255, null=True)),
                ('string_2', models.CharField(blank=True, max_length=255, null=True)),
                ('string_3', models.CharField(blank=True, max_length=255, null=True)),
                ('string_4', models.CharField(blank=True, max_length=255, null=True)),
                ('string_5', models.CharField(blank=True, max_length=255, null=True)),
                ('string_6', models.CharField(blank=True, max_length=255, null=True)),
                ('string_7', models.CharField(blank=True, max_length=255, null=True)),
                ('string_8', models.CharField(blank=True, max_length=255, null=True)),
                ('string_9', models.CharField(blank=True, max_length=255, null=True)),
                ('string_10', models.CharField(blank=True, max_length=255, null=True)),
                ('string_11', models.CharField(blank=True, max_length=255, null=True)),
                ('string_12', models.CharField(blank=True, max_length=255, null=True)),
                ('string_13', models.CharField(blank=True, max_length=255, null=True)),
                ('string_14', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Member',
                'ordering': ['guid'],
            },
        ),
        migrations.CreateModel(
            name='MemberGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('flat_discount_percentage', models.FloatField(default=0)),
                ('can_be_parent', models.BooleanField(default=True)),
                ('default_group', models.BooleanField(default=False)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Member Group',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sold_by', models.CharField(choices=[('item', 'item'), ('weight', 'weight')], default='item', max_length=6)),
                ('vat_applicable', models.BooleanField(default=True)),
                ('image', models.CharField(blank=True, max_length=70, null=True)),
                ('inventory_flag', models.BooleanField(default=True)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('attribute_1', models.ManyToManyField(related_name='product_attr_1', to='saleboxecomdjango.AttributeItem')),
                ('attribute_2', models.ManyToManyField(related_name='product_attr_2', to='saleboxecomdjango.AttributeItem')),
            ],
            options={
                'verbose_name': 'Product',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=100)),
                ('image', models.CharField(default='/static/backoffice/product.png', max_length=70)),
                ('seasonal_flag', models.BooleanField(default=False)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='saleboxecomdjango.ProductCategory')),
            ],
            options={
                'verbose_name': 'Product Category',
                'ordering': ['name'],
                'verbose_name_plural': 'Product Categories',
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default='', max_length=150)),
                ('bo_name', models.CharField(blank=True, default='', max_length=200)),
                ('plu', models.CharField(blank=True, default='', max_length=25)),
                ('sku', models.CharField(blank=True, default='', max_length=25)),
                ('color', models.CharField(blank=True, default='', max_length=50)),
                ('size', models.CharField(blank=True, default='', max_length=20)),
                ('size_order', models.FloatField(default=0)),
                ('size_uom', models.CharField(blank=True, choices=[('', 'n/a'), ('g', 'g'), ('kg', 'kg'), ('ml', 'ml')], default='', max_length=2)),
                ('price', models.IntegerField()),
                ('barcode', models.CharField(blank=True, default='', max_length=50)),
                ('available_to_order', models.BooleanField(default=True)),
                ('available_on_pos', models.BooleanField(default=True)),
                ('available_on_ecom', models.BooleanField(default=True)),
                ('shelf_expiry_type', models.CharField(default='manual', max_length=12)),
                ('shelf_life_days', models.IntegerField(blank=True, null=True)),
                ('image', models.CharField(blank=True, max_length=70, null=True)),
                ('unique_string', models.CharField(max_length=255)),
                ('shipping_weight', models.IntegerField(blank=True, null=True)),
                ('loyalty_points', models.FloatField(blank=True, null=True)),
                ('member_discount_applicable', models.BooleanField(default=True)),
                ('string_1', models.CharField(blank=True, max_length=50, null=True)),
                ('string_2', models.CharField(blank=True, max_length=50, null=True)),
                ('string_3', models.CharField(blank=True, max_length=50, null=True)),
                ('string_4', models.CharField(blank=True, max_length=50, null=True)),
                ('warehouse_location', models.CharField(blank=True, max_length=50, null=True)),
                ('int_1', models.IntegerField(blank=True, null=True)),
                ('int_2', models.IntegerField(blank=True, null=True)),
                ('int_3', models.IntegerField(blank=True, null=True)),
                ('int_4', models.IntegerField(blank=True, null=True)),
                ('date_1', models.DateField(blank=True, null=True)),
                ('date_2', models.DateField(blank=True, null=True)),
                ('active_flag', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
                ('attribute_1', models.ManyToManyField(related_name='variant_attr_1', to='saleboxecomdjango.AttributeItem')),
                ('attribute_2', models.ManyToManyField(related_name='variant_attr_2', to='saleboxecomdjango.AttributeItem')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.Product')),
            ],
            options={
                'verbose_name': 'Product Variant',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.ProductCategory'),
        ),
        migrations.AddField(
            model_name='member',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.MemberGroup'),
        ),
        migrations.AddField(
            model_name='member',
            name='group_when_created',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='group_when_created', to='saleboxecomdjango.MemberGroup'),
        ),
        migrations.AddField(
            model_name='member',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='saleboxecomdjango.Member'),
        ),
        migrations.AddField(
            model_name='discountruleset',
            name='product_variant',
            field=models.ManyToManyField(blank=True, to='saleboxecomdjango.ProductVariant'),
        ),
    ]
