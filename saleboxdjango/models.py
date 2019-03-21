import uuid

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.cache import cache
from django.db import models
from django.db.models import Avg

from mptt.models import MPTTModel, TreeForeignKey
from saleboxdjango.lib.common import get_price_display, get_rating_display


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
    slug = models.CharField(max_length=100, blank=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    delete_dt = models.DateTimeField(blank=True, null=True)
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
        verbose_name_plural = 'Country States'


class CountryStateTranslation(models.Model):
    language = models.CharField(max_length=7)
    state = models.ForeignKey(CountryState, blank=True, null=True, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['language', 'state']
        verbose_name = 'Country State Translations'


class CountryTranslation(models.Model):
    language = models.CharField(max_length=7)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    value = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['language', 'country']
        verbose_name = 'Country Translations'


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


class LastUpdate(models.Model):
    code = models.CharField(max_length=36)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return self.code

    class Meta:
        ordering = ['code']
        verbose_name = 'Last Update'


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
    local_image = models.CharField(max_length=25, blank=True, null=True)
    seasonal_flag = models.BooleanField(default=False)
    slug = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    slug_path = models.CharField(max_length=255, blank=True, null=True, db_index=True)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        root = self.get_root()
        nodes = root.get_descendants(include_self=True)
        for node in nodes:
            slugs = node.get_ancestors(include_self=True).values_list('slug', flat=True)
            slugs = ['' if s is None else s for s in slugs]
            slug_path = '/'.join(slugs)
            if node.slug_path != slug_path:
                ProductCategory.objects.filter(id=node.id).update(slug_path=slug_path)
        cache.delete('category_tree')


class Product(models.Model):
    SOLD_BY_CHOICES = (
        ('item', 'item'),
        # ('volume', 'volume'),
        ('weight', 'weight'),
    )
    category = models.ForeignKey(ProductCategory, blank=True, null=True,on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    attribute_1 = models.ManyToManyField(AttributeItem, related_name='product_attr_1', blank=True)
    attribute_2 = models.ManyToManyField(AttributeItem, related_name='product_attr_2', blank=True)
    attribute_3 = models.ManyToManyField(AttributeItem, related_name='product_attr_3', blank=True)
    attribute_4 = models.ManyToManyField(AttributeItem, related_name='product_attr_4', blank=True)
    attribute_5 = models.ManyToManyField(AttributeItem, related_name='product_attr_5', blank=True)
    attribute_6 = models.ManyToManyField(AttributeItem, related_name='product_attr_6', blank=True)
    attribute_7 = models.ManyToManyField(AttributeItem, related_name='product_attr_7', blank=True)
    attribute_8 = models.ManyToManyField(AttributeItem, related_name='product_attr_8', blank=True)
    attribute_9 = models.ManyToManyField(AttributeItem, related_name='product_attr_9', blank=True)
    attribute_10 = models.ManyToManyField(AttributeItem, related_name='product_attr_10', blank=True)
    string_1 = models.CharField(max_length=150, blank=True, null=True)
    string_2 = models.CharField(max_length=150, blank=True, null=True)
    string_3 = models.CharField(max_length=150, blank=True, null=True)
    string_4 = models.CharField(max_length=150, blank=True, null=True)
    sold_by = models.CharField(max_length=6, choices=SOLD_BY_CHOICES, default='item')
    vat_applicable = models.BooleanField(default=True)
    image = models.CharField(max_length=70, blank=True, null=True)
    local_image = models.CharField(max_length=25, blank=True, null=True)
    inventory_flag = models.BooleanField(default=True)
    # season = models.ForeignKey(OrganizationSeason, null=True, blank=True)
    slug = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    bestseller_rank = models.IntegerField(default=0)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # local values
    rating_score = models.IntegerField(default=0)
    rating_vote_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'

    def delete(self):
        pass

    def update_rating(self):
        self.rating_score = \
            ProductVariant \
                .objects \
                .filter(product=self) \
                .aggregate(rating=Avg('rating_score'))['rating']
        self.rating_vote_count = \
            ProductVariant \
                .objects \
                .filter(product=self) \
                .count()
        self.save()


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
    sale_price = models.IntegerField(default=0)
    sale_percent = models.IntegerField(default=0)
    barcode = models.CharField(max_length=50, blank=True, default='')
    available_to_order = models.BooleanField(default=True)
    available_on_pos = models.BooleanField(default=True)
    available_on_ecom = models.BooleanField(default=True)
    shelf_expiry_type = models.CharField(max_length=12, default='manual')
    shelf_life_days = models.IntegerField(blank=True, null=True)
    slug = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    image = models.CharField(max_length=70, blank=True, null=True)
    local_image = models.CharField(max_length=20, blank=True, null=True)
    unique_string = models.CharField(max_length=255, blank=True)
    shipping_weight = models.IntegerField(blank=True, null=True)
    loyalty_points = models.FloatField(blank=True, null=True)
    member_discount_applicable = models.BooleanField(default=True)
    string_1 = models.CharField(max_length=150, blank=True, null=True)
    string_2 = models.CharField(max_length=150, blank=True, null=True)
    string_3 = models.CharField(max_length=150, blank=True, null=True)
    string_4 = models.CharField(max_length=150, blank=True, null=True)
    warehouse_location = models.CharField(max_length=50, blank=True, null=True)
    int_1 = models.IntegerField(blank=True, null=True)
    int_2 = models.IntegerField(blank=True, null=True)
    int_3 = models.IntegerField(blank=True, null=True)
    int_4 = models.IntegerField(blank=True, null=True)
    date_1 = models.DateField(blank=True, null=True)
    date_2 = models.DateField(blank=True, null=True)
    attribute_1 = models.ManyToManyField(AttributeItem, related_name='variant_attr_1', blank=True)
    attribute_2 = models.ManyToManyField(AttributeItem, related_name='variant_attr_2', blank=True)
    attribute_3 = models.ManyToManyField(AttributeItem, related_name='variant_attr_3', blank=True)
    attribute_4 = models.ManyToManyField(AttributeItem, related_name='variant_attr_4', blank=True)
    attribute_5 = models.ManyToManyField(AttributeItem, related_name='variant_attr_5', blank=True)
    attribute_6 = models.ManyToManyField(AttributeItem, related_name='variant_attr_6', blank=True)
    attribute_7 = models.ManyToManyField(AttributeItem, related_name='variant_attr_7', blank=True)
    attribute_8 = models.ManyToManyField(AttributeItem, related_name='variant_attr_8', blank=True)
    attribute_9 = models.ManyToManyField(AttributeItem, related_name='variant_attr_9', blank=True)
    attribute_10 = models.ManyToManyField(AttributeItem, related_name='variant_attr_10', blank=True)
    active_flag = models.BooleanField(default=True)
    ecommerce_description = models.TextField(blank=True, null=True)
    bestseller_rank = models.IntegerField(default=0)
    default_image = models.CharField(max_length=35, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    # local values
    rating_score = models.IntegerField(default=0)
    rating_vote_count = models.IntegerField(default=0)


    def __str__(self):
        return self.name or ''

    class Meta:
        ordering = ['id']
        verbose_name = 'Product Variant'

    def delete(self):
        pass

    def price_display(self):
        return get_price_display(self.price)

    def rating_display(self):
        return get_rating_display(self.rating_score, self.rating_vote_count)

    def sale_price_display(self):
        return get_price_display(self.sale_price)

    def save(self, *args, **kwargs):
        self.default_image = None

        # attempt to use first variant image
        pvi = ProductVariantImage \
                .objects \
                .filter(variant=self) \
                .filter(local_img__isnull=False) \
                .order_by('order') \
                .first()
        if pvi is not None:
            self.default_image = 'pvi/%s' % pvi.local_img

        # fallback to POS image if that exists
        if self.default_image is None and self.local_image is not None:
            self.default_image = 'pospv/%s' % self.local_image

        # save
        super(ProductVariant, self).save(*args, **kwargs)


    def update_rating(self):
        self.rating_score = \
            ProductVariantRating \
                .objects \
                .filter(variant=self) \
                .aggregate(rating=Avg('rating'))['rating'] or 0
        self.rating_vote_count = \
            ProductVariantRating \
                .objects \
                .filter(variant=self) \
                .count()
        self.save()
        self.product.update_rating()


class ProductVariantImage(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    img = models.CharField(max_length=100, default='')
    local_img = models.CharField(max_length=25, blank=True, null=True)
    img_height = models.IntegerField(default=0)
    img_width = models.IntegerField(default=0)
    title = models.CharField(max_length=150, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    active_flag = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('order',)

    def save(self, *args, **kwargs):
        super(ProductVariantImage, self).save(*args, **kwargs)
        self.variant.save()


class ProductVariantRating(models.Model):
    variant = models.ForeignKey('ProductVariant', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=50)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Variant Rating'

    def delete(self, *args, **kwargs):
        variant = self.variant
        super().delete(*args, **kwargs)
        self.variant.update_rating()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.variant.update_rating()


class UserAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    default = models.BooleanField(default=False)
    address_group = models.CharField(max_length=10, default='default')
    full_name = models.CharField(max_length=150)
    address_1 = models.CharField(max_length=150)
    address_2 = models.CharField(max_length=150, blank=True, null=True)
    address_3 = models.CharField(max_length=150, blank=True, null=True)
    address_4 = models.CharField(max_length=150, blank=True, null=True)
    address_5 = models.CharField(max_length=150, blank=True, null=True)
    country_state = models.ForeignKey(CountryState, blank=True, null=True, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.CASCADE)
    postcode = models.CharField(max_length=12, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s, %s...' % (self.full_name, self.address_1)

    class Meta:
        ordering = ['-default', 'full_name', 'address_1']
        verbose_name = 'User Address'

    def delete(self, *args, **kwargs):
        user = self.user
        address_type = self.address_group
        super().delete(*args, **kwargs)
        self.ensure_one_default_exists(user, address_group)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_one_default_exists(self.user, self.address_group)

    def ensure_one_default_exists(self, user, address_group):
        addresses = UserAddress \
                        .objects \
                        .filter(user=user) \
                        .filter(address_group=address_group) \
                        .order_by('-last_update')

        if len(addresses) > 0:
            default_count = 0
            for a in addresses:
                if a.default:
                    default_count += 1
                    if default_count > 1:
                        a.default = False
                        a.save()

            if default_count == 0:
                addresses[0].default = True
                addresses[0].save()
