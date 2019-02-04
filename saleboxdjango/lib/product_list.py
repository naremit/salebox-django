import math

from django.conf import settings
from django.core.cache import cache
from django.db.models import Case, F, Value, When
from django.http import Http404

from saleboxdjango.lib.common import fetchsinglevalue, \
    dictfetchall, image_path
from saleboxdjango.models import Attribute, AttributeItem, Product, ProductCategory, ProductVariant




class ProductList:
    def __init__(self, active_status='active_only'):
        # product filters
        self.query = ProductVariant.objects
        self.active_status = active_status
        self.min_price = None
        self.max_price = None
        self.order = []

        # pagination
        self.offset = 0
        self.page_numberber = 1
        self.limit = 50
        self.items_per_page = 50
        self.pagination_url_prefix = ''

        # misc
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
            variant_ids = list(
                self.query
                    .order_by('product__id', 'price') \
                    .distinct('product__id') \
                    .values_list('id', flat=True)
            )

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
                'previous': self.page_number + 1,
                'has_next': self.page_number < number_of_pages,
                'next': self.page_number - 1,
                'url_prefix': self.pagination_url_prefix
            },
            'products': self.retrieve_in_basket_flags(request, data['qs'])
        }


    def get_single(self, request, id, slug):
        pass


    def retrieve_in_basket_flags(self, request, variants):
        for pv in variants:
            pv.in_basket = str(pv.id) in \
                request.session['basket']['basket']['contents']
            pv.in_wishlist = str(pv.id) in \
                request.session['basket']['wishlist']['contents']

        return variants


    def retrieve_results(self, variant_ids):
        self.set_active_status()

        qs = []
        if len(variant_ids) > 0:
            qs = ProductVariant \
                    .objects \
                    .filter(id__in=variant_ids) \
                    .select_related('product', 'product__category')

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
                # TODO: use local image if available
                #
                #
                o.image = '%s%s' % (
                    settings.SALEBOX['IMG']['POSASSETS'],
                    o.image
                )

                # flat discount modifiers
                try:
                    if o.modified_price:
                        o.sale_price = o.modified_price
                        del o.modified_price
                except:
                    pass

        return qs


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


    def set_flat_discount(self, percent):
        self.flat_discount = percent


    def set_flat_member_discount(self, percent):
        self.flat_member_discount = percent


    def set_pagination(self, page_number, items_per_page, url_prefix):
        self.page_number = page_number
        self.offset = (page_number - 1) * items_per_page
        self.limit = self.offset + items_per_page
        self.items_per_page = items_per_page
        self.pagination_url_prefix = url_prefix


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


def get_category_tree(root=None):
    # fetch from cache
    cached_tree = cache.get('category_tree')
    if cached_tree is not None:
        return get_category_tree_segment_dict(root, cached_tree)

    # extract root node(s)
    tree = []
    categories = ProductCategory \
                    .objects \
                    .filter(active_flag=True) \
                    .order_by('name')
    for c in categories:
        if c.is_root_node():
            tree.append(c)

    # build children
    tree = [get_category_tree_recurse(c) for c in tree]

    # finish up
    cache.set('category_tree', tree, 60 * 60 * 24 * 7)

    # return tree segment
    return get_category_tree_segment_dict(root, tree)


def get_category_tree_segment_dict(root, tree):
    o = {
        'root_level': root is None,
        'ancestors': [],
        'category': get_category_tree_segment(root, tree)
    }

    if root is not None:
        o['category'] = [o['category']]
        ancestors = root.get_ancestors(include_self=False)
        for a in ancestors:
            o['ancestors'].append({
                'id': a.id,
                'short_name': a.short_name,
                'name': a.name,
                'image': image_path(a.image),
                'slug': a.slug,
                'slug_path': a.slug_path,
            })

    return o


def get_category_tree_segment(root, tree):
    if root is None:
        return tree
    else:
        for subtree in tree:
            result = get_category_tree_segment_recurse(root, subtree)
            if result is not None:
                return result

        return None


def get_category_tree_segment_recurse(root, tree):
    if root.id == tree['id']:
        return tree
    else:
        for subtree in tree['children']:
            result = get_category_tree_segment_recurse(root, subtree)
            if result is not None:
                return result

    return None


def get_category_tree_recurse(c):
    product_ids = ProductVariant \
                    .objects \
                    .filter(product__category=c) \
                    .filter(product__active_flag=True) \
                    .filter(active_flag=True) \
                    .filter(available_on_ecom=True) \
                    .values_list('product_id', flat=True)

    children = c.get_children().filter(active_flag=True).order_by('name')
    return {
        'id': c.id,
        'short_name': c.short_name,
        'name': c.name,
        'image': image_path(c.image),
        'product_count': len(set(list(product_ids))),
        'slug': c.slug,
        'slug_path': c.slug_path,
        'children': [get_category_tree_recurse(c) for c in children]
    }


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
