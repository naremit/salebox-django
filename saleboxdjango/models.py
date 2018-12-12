import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Attribute(models.Model):
    code = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['code']
        verbose_name = 'Product Attribute'

    def delete(self):
        pass


class AttributeItem(models.Model):
    attribute = models.ForeignKey(Attribute, blank=True, null=True, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.value

    class Meta:
        ordering = ['value']
        verbose_name = 'Product Attribute Item'

    def delete(self):
        pass


class BasketWishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    session = models.CharField(max_length=32, blank=True, null=True)
    basket_flag = models.BooleanField(default=True)
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    weight = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)


class Country(models.Model):
    code_2 = models.CharField(max_length=2, blank=True, null=True)
    code_3 = models.CharField(max_length=3, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Countries'


class CountryState(models.Model):
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    code_2 = models.CharField(max_length=2, blank=True, null=True)
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class DiscountGroup(models.Model):
    GROUP_TYPE_CHOICES = (
        ('S', 'Seasonal'),
        ('M', 'Manual')
    )
    FIELD_CHOICES = (
        (0, 'Inactive'),
        (1, 'Active, not required'),
        (2, 'Active, required'),
    )
    ROUNDING_CHOICES = (
        ('none', 'No rounding'),
        ('up_major_1', 'Round UP to nearest major unit'),
        ('up_major_5', 'Round UP to nearest major unit multiple of 5'),
        ('up_major_10', 'Round UP to nearest major unit multiple of 10'),
    )
    name = models.CharField(max_length=25)
    group_type = models.CharField(max_length=1, default='M', choices=GROUP_TYPE_CHOICES)
    operational_flag = models.BooleanField(default=False)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Discount Group'

    def delete(self):
        pass


class DiscountRuleset(models.Model):
    TYPE_CHOICES = (
        ('flat_percent', 'Flat Percentage'),
    )
    group = models.ForeignKey(DiscountGroup, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=25)
    discount_type = models.CharField(default='flat_percent', max_length=12, choices=TYPE_CHOICES)
    value = models.IntegerField(null=True, blank=True)
    start_dt = models.DateTimeField(null=True, blank=True)
    end_dt = models.DateTimeField(null=True, blank=True)
    product_variant = models.ManyToManyField('ProductVariant', blank=True)
    operational_flag = models.BooleanField(default=True)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Discount Ruleset'

    def delete(self):
        pass


class EmailValidator(models.Model):
    ACTION_CHOICES = (
        ('e', 'Change Email'),
        ('f', 'Forgot Password'),
        ('r', 'Register'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    hash_string = models.CharField(max_length=64, default='')
    data = JSONField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s%s' % (self.id, self.action)

    def get_hash(self):
        return '%s%s' % (self.id, self.hash_string)

    def save(self, *args, **kwargs):
        if len(self.hash_string) < 64:
            self.hash_string = '%s%s' % (uuid.uuid4().hex, uuid.uuid4().hex)
        super().save(*args, **kwargs)


class MemberGroup(models.Model):
    name = models.CharField(max_length=50)
    flat_discount_percentage = models.FloatField(default=0)
    can_be_parent = models.BooleanField(default=True)
    default_group = models.BooleanField(default=False)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Member Group'

    def delete(self):
        pass


class Member(models.Model):
    TITLE_CHOICES = (
        (1, 'Mr'),
        (2, 'Mrs'),
        (3, 'Miss'),
    )
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unspecified'),
    )
    STATUS_CHOICES = (
        ('A', 'Active'),
        ('R', 'Resigned'),
        ('S', 'Suspended'),
        ('T', 'Terminated'),
    )
    # id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(MemberGroup, null=True, blank=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('Member', null=True, blank=True, on_delete=models.CASCADE)
    guid = models.CharField(max_length=25, db_index=True)
    gender = models.CharField(max_length=1, blank=True, null=True, choices=GENDER_CHOICES)
    title = models.IntegerField(blank=True, null=True, choices=TITLE_CHOICES)
    name_first = models.CharField(max_length=20, blank=True, null=True)
    name_last = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    address_3 = models.CharField(max_length=255, blank=True, null=True)
    address_4 = models.CharField(max_length=255, blank=True, null=True)
    address_5 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=12, blank=True, null=True)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    country_state = models.ForeignKey(CountryState, blank=True, null=True, on_delete=models.CASCADE)
    phone_1 = models.CharField(max_length=20, blank=True, null=True)
    phone_2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    id_card = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=1, default='A', choices=STATUS_CHOICES)
    active_flag = models.BooleanField(default=True)
    join_date = models.DateField(blank=True, null=True)
    string_1 = models.CharField(max_length=255, blank=True, null=True)
    string_2 = models.CharField(max_length=255, blank=True, null=True)
    string_3 = models.CharField(max_length=255, blank=True, null=True)
    string_4 = models.CharField(max_length=255, blank=True, null=True)
    string_5 = models.CharField(max_length=255, blank=True, null=True)
    string_6 = models.CharField(max_length=255, blank=True, null=True)
    string_7 = models.CharField(max_length=255, blank=True, null=True)
    string_8 = models.CharField(max_length=255, blank=True, null=True)
    string_9 = models.CharField(max_length=255, blank=True, null=True)
    string_10 = models.CharField(max_length=255, blank=True, null=True)
    string_11 = models.CharField(max_length=255, blank=True, null=True)
    string_12 = models.CharField(max_length=255, blank=True, null=True)
    string_13 = models.CharField(max_length=255, blank=True, null=True)
    string_14 = models.CharField(max_length=255, blank=True, null=True)
    group_when_created = models.ForeignKey(MemberGroup, blank=True, null=True, related_name='group_when_created', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.guid

    class Meta:
        ordering = ['guid']
        verbose_name = 'Member'

    def delete(self):
        pass


class ProductCategory(MPTTModel):
    short_name = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True, on_delete=models.CASCADE)
    image = models.CharField(max_length=70, blank=True, null=True)
    seasonal_flag = models.BooleanField(default=False)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Product Category'
        verbose_name_plural = 'Product Categories'

    def delete(self):
        pass


class Product(models.Model):
    SOLD_BY_CHOICES = (
        ('item', 'item'),
        # ('volume', 'volume'),
        ('weight', 'weight'),
    )
    category = models.ForeignKey(ProductCategory, blank=True, null=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    attribute_1 = models.ManyToManyField(AttributeItem, related_name='product_attr_1')
    attribute_2 = models.ManyToManyField(AttributeItem, related_name='product_attr_2')
    sold_by = models.CharField(max_length=6, choices=SOLD_BY_CHOICES, default='item')
    vat_applicable = models.BooleanField(default=True)
    image = models.CharField(max_length=70, blank=True, null=True)
    inventory_flag = models.BooleanField(default=True)
    # season = models.ForeignKey(OrganizationSeason, null=True, blank=True)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'

    def delete(self):
        pass


class ProductRatingCache(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    vote_count = models.IntegerField(default=1)
    rating = models.IntegerField(default=50)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Rating Cache'
        verbose_name_plural = 'Product Rating Cache'


class ProductVariantRating(models.Model):
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=50)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Variant Rating'

    def delete(self, *args, **kwargs):
        product = self.variant.product
        super().delete(*args, **kwargs)
        self.update_cache(product)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_cache(self.variant.product)

    def update_cache(self, product):
        # create / update product cache
        o, created = ProductRatingCache \
                        .objects \
                        .get_or_create(product=product)

        # calculate rating
        if created:
            o.vote_count = 1
            o.rating = self.rating
        else:
            vote_count = 0
            sum_rating = 0
            ratings = ProductVariantRating \
                        .objects \
                        .filter(variant=self.variant)

            for r in ratings:
                vote_count += 1
                sum_rating += r.rating

            o.vote_count = vote_count
            if vote_count > 0:
                o.rating = round(sum_rating / vote_count)
            else:
                o.rating = 0

        # save
        o.save()


class ProductVariant(models.Model):
    SHELF_EXPIRY_CHOICES = (
        ('none', 'No shelf expiry date'),
        ('manual', 'Enter shelf expiry date manually'),
        ('delivery', 'Calculate from delivery date'),
        ('manufacture', 'Calculate from manufacture date'),
    )
    SIZE_UOM_CHOICES = (
        ('', 'n/a'),
        ('g', 'g'),
        ('kg', 'kg'),
        ('ml', 'ml'),
    )
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=True, default='')
    bo_name = models.CharField(max_length=200, blank=True, default='')
    plu = models.CharField(max_length=25, blank=True, default='')
    sku = models.CharField(max_length=25, blank=True, default='')
    color = models.CharField(max_length=50, blank=True, default='')
    size = models.CharField(max_length=20, blank=True, default='')
    size_order = models.FloatField(default=0)
    size_uom = models.CharField(max_length=2, choices=SIZE_UOM_CHOICES, blank=True, default='')
    price = models.IntegerField(null=True)
    barcode = models.CharField(max_length=50, blank=True, default='')
    available_to_order = models.BooleanField(default=True)
    available_on_pos = models.BooleanField(default=True)
    available_on_ecom = models.BooleanField(default=True)
    shelf_expiry_type = models.CharField(max_length=12, default='manual')
    shelf_life_days = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(max_length=100, blank=True, null=True)
    image = models.CharField(max_length=70, blank=True, null=True)
    unique_string = models.CharField(max_length=255)
    shipping_weight = models.IntegerField(blank=True, null=True)
    loyalty_points = models.FloatField(blank=True, null=True)
    member_discount_applicable = models.BooleanField(default=True)
    string_1 = models.CharField(max_length=50, blank=True, null=True)
    string_2 = models.CharField(max_length=50, blank=True, null=True)
    string_3 = models.CharField(max_length=50, blank=True, null=True)
    string_4 = models.CharField(max_length=50, blank=True, null=True)
    warehouse_location = models.CharField(max_length=50, blank=True, null=True)
    int_1 = models.IntegerField(blank=True, null=True)
    int_2 = models.IntegerField(blank=True, null=True)
    int_3 = models.IntegerField(blank=True, null=True)
    int_4 = models.IntegerField(blank=True, null=True)
    date_1 = models.DateField(blank=True, null=True)
    date_2 = models.DateField(blank=True, null=True)
    attribute_1 = models.ManyToManyField(AttributeItem, related_name='variant_attr_1')
    attribute_2 = models.ManyToManyField(AttributeItem, related_name='variant_attr_2')
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or ''

    class Meta:
        ordering = ['id']
        verbose_name = 'Product Variant'

    def delete(self):
        pass


class LastUpdate(models.Model):
    code = models.CharField(max_length=36)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['code']
        verbose_name = 'Last Update'
