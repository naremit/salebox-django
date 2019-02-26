import math

from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, F, Value, When
from django.http import Http404

from saleboxdjango.lib.common import fetchsinglevalue, \
    dictfetchall, get_rating_display

from saleboxdjango.models import Attribute, AttributeItem, \
    Product, ProductCategory, ProductVariant, ProductVariantRating


class SaleboxProduct:
    def __init__(self, active_status='active_only'):
        # product filters
        self.query = ProductVariant.objects
        self.active_status = active_status
        self.min_price = None
        self.max_price = None
        self.order = []
        self.prefetch_product_attributes = []
        self.prefetch_variant_attributes = []

        # pagination
        self.offset = 0
        self.page_numberber = 1
        self.limit = 50
        self.items_per_page = 50
        self.pagination_url_prefix = ''

        # misc
        self.fetch_user_ratings = True
        self.flat_discount = 0
        self.flat_member_discount = 0

    def get_list(self, request):
        # TODO: retrieve from cache
        #
        #
        data = None

        # cache doesn't exist, build it...
        if data is None:
            # retrieve list of variant IDs (one variant per product)
            # which match our criteria
            self.query = \
                self.query \
                    .order_by('product__id', 'price') \
                    .distinct('product__id') \
                    .values_list('id', flat=True)

            variant_ids = self.retrieve_variant_ids()

            data = {
                'variant_ids': variant_ids,
                'qs': self.retrieve_results(variant_ids)
            }

            # TODO: save data to cache
            #
            #

        # pagination calculations
        number_of_pages = math.ceil(len(data['variant_ids']) / self.items_per_page)

        # create output dict
        return {
            'count': {
                'from': self.offset + 1,
                'to': self.offset + len(data['qs']),
                'total': len(data['variant_ids']),
            },
            'pagination': {
                'page_number': self.page_number,
                'number_of_pages': number_of_pages,
                'page_range': range(1, number_of_pages + 1),
                'has_previous': self.page_number > 1,
                'previous': self.page_number - 1,
                'has_next': self.page_number < number_of_pages,
                'next': self.page_number + 1,
                'url_prefix': self.pagination_url_prefix
            },
            'products': self.retrieve_user_interaction(request, data['qs'])
        }

    def get_single(self, request, id, slug):
        self.query = \
            self.query \
                .filter(id=id) \
                .filter(slug=slug) \
                .values_list('id', flat=True)

        # ensure variant exists
        variant_ids = self.retrieve_variant_ids()
        if len(variant_ids) == 0:
            raise Http404

        # retrieve variant
        return self.retrieve_user_interaction(
            request,
            self.retrieve_results(variant_ids)
        )[0]

    def retrieve_results(self, variant_ids):
        qs = []
        if len(variant_ids) > 0:
            qs = ProductVariant \
                    .objects \
                    .filter(id__in=variant_ids) \
                    .select_related('product', 'product__category')

            # prefetch attributes
            if len(self.prefetch_product_attributes) > 0:
                qs = qs.prefetch_related(*self.prefetch_product_attributes)
            if len(self.prefetch_variant_attributes) > 0:
                qs = qs.prefetch_related(*self.prefetch_variant_attributes)

            # price modifier: flat_discount
            if self.flat_discount > 0:
                ratio = 1 - (self.flat_discount / 100)
                qs = qs.annotate(
                    modified_price=F('price') * ratio
                )

            # price modifier: flat_member_discount
            if self.flat_member_discount > 0:
                ratio = 1 - (self.flat_member_discount / 100)
                qs = qs.annotate(modified_price=Case(
                    When(
                        member_discount_applicable=True,
                        then=F('price') * ratio
                    ),
                    default=F('price')
                ))

            # add ordering
            if len(self.order) > 0:
                if (
                    self.flat_discount > 0 or
                    self.flat_member_discount > 0
                ):
                    self.order = [
                        o.replace('sale_price', 'modified_price')
                        for o in self.order
                    ]
                qs = qs.order_by(*self.order)

            # add offset / limit
            qs = qs[self.offset:self.limit]

            # modify results
            for o in qs:
                # flat discount modifiers
                try:
                    if o.modified_price:
                        o.sale_price = o.modified_price
                        del o.modified_price
                except:
                    pass

        return qs

    def retrieve_user_interaction(self, request, variants):
        # get user ratings
        rating_dict = {}
        if self.fetch_user_ratings and request.user.is_authenticated:
            ratings = ProductVariantRating \
                        .objects \
                        .filter(variant__id__in=[pv.id for pv in variants]) \
                        .filter(user=request.user)
            for r in ratings:
                rating_dict[r.variant.id] = r.rating

        # get basket / wishlist flags
        for pv in variants:
            try:
                pv.basket_qty = \
                    request.session['basket']['basket']['contents'][str(pv.id)]
            except:
                pv.basket_qty = 0

            pv.in_wishlist = str(pv.id) in \
                request.session['basket']['wishlist']['contents']

            if pv.id in rating_dict:
                pv.user_rating = get_rating_display(rating_dict[pv.id], 1)
            else:
                pv.user_rating = None

        return variants

    def retrieve_variant_ids(self):
        self.set_active_status()
        return list(self.query)

    def set_prefetch_product_attributes(self, numbers):
        if isinstance(numbers, int):
            numbers = [numbers]
        self.prefetch_product_attributes = [
            'product__attribute_%s' % i for i in numbers
        ]

    def set_prefetch_variant_attributes(self, numbers):
        if isinstance(numbers, int):
            numbers = [numbers]
        self.prefetch_variant_attributes = [
            'attribute_%s' % i for i in numbers
        ]

    def set_active_status(self):
        # I can think of no reason for this to ever be set to anything
        # other than 'active_only' but include this here so it doesn't
        # bite us later
        if self.active_status == 'active_only':
            self.query = \
                self.query \
                    .filter(active_flag=True) \
                    .filter(available_on_ecom=True) \
                    .filter(product__active_flag=True) \
                    .filter(product__category__active_flag=True)

        elif self.active_status == 'all':
            pass

    def set_category(self, category, include_child_categories=True):
        if include_child_categories:
            id_list = category \
                        .get_descendants(include_self=True) \
                        .values_list('id', flat=True)
        else:
            id_list = [category.id]

        self.query = self.query.filter(product__category__in=id_list)

    def set_fetch_user_ratings(self, value):
        self.fetch_user_ratings = value

    def set_flat_discount(self, percent):
        self.flat_discount = percent

    def set_flat_member_discount(self, percent):
        self.flat_member_discount = percent

    def set_max_price(self, maximun):
        self.query = self.query.filter(sale_price__lte=maximun)

    def set_min_price(self, minimun):
        self.query = self.query.filter(sale_price__gte=minimum)

    def set_order_preset(self, preset):
        # so... it turns out having multiple ORDER BYs with a LIMIT
        # clause slows things down a lot.
        self.order = {
            'bestseller_low_to_high': ['bestseller_rank'],
            'bestseller_high_to_low': ['-bestseller_rank'],
            'price_low_to_high': ['sale_price'],
            'price_high_to_low': ['-sale_price'],
            'rating_low_to_high': ['rating_score'],
            'rating_high_to_low': ['-rating_score'],
        }[preset]

    def set_pagination(self, page_number, items_per_page, url_prefix):
        self.page_number = page_number
        self.offset = (page_number - 1) * items_per_page
        self.limit = self.offset + items_per_page
        self.items_per_page = items_per_page
        self.pagination_url_prefix = url_prefix

    def set_product_attribute_include(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.query = self.query.filter(**{key: value})

    def set_product_attribute_include_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'product__attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.query = self.query.filter(**{key: field_value})

    def set_product_attribute_exclude(self, attribute_number, value):
        key = 'product__attribute_%s' % attribute_number
        self.query = self.query.exclude(**{key: value})

    def set_product_attribute_exclude_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'product__attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.query = self.query.exclude(**{key: field_value})

    def set_variant_attribute_include(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.query = self.query.filter(**{key: value})

    def set_variant_attribute_include_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.query = self.query.filter(**{key: field_value})

    def set_variant_attribute_exclude(self, attribute_number, value):
        key = 'attribute_%s' % attribute_number
        self.query = self.query.exclude(**{key: value})

    def set_variant_attribute_exclude_keyvalue(
            self,
            attribute_number,
            field_name,
            field_value,
            field_modifier=None
        ):
        key = 'attribute_%s__%s' % (attribute_number, field_name)
        if field_modifier is not None:
            key = '%s__%s' % (key, field_modifier)
        self.query = self.query.exclude(**{key: field_value})


def translate_path(path):
    o = {}
    o['path_list'] = path.strip('/').split('/')

    try:
        o['page_number'] = int(o['path_list'][-1])
        if o['page_number'] < 1:
            raise Http404()
        o['path_list'] = o['path_list'][:-1]
        if len(o['path_list']) == 0:
            o['path_list'].append('')
    except:
        o['page_number'] = 1

    o['path'] = '/'.join(o['path_list'])
    return o
