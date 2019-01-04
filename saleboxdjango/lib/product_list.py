import math

from django.core.cache import cache
from django.http import Http404

from saleboxdjango.lib.common import fetchsinglevalue, \
    dictfetchall, image_path, price_display, get_rating_dict
from saleboxdjango.models import Attribute, AttributeItem, Product, ProductCategory, ProductRatingCache, ProductVariant

"""

"""


class ProductList:
    def __init__(self):
        self.include_pagination = False
        self.pagination = {
            'page_num': None,
            'items_per_page': None,
            'num_of_pages': None,
            'page_range': None,
            'url_prefix': None,
            'has_previous': False,
            'has_next': False,
        }

        self.member_discount_active = False
        self.member_discount_rate = 0

        self.include_rating = False
        self.offset = None
        self.limit = None
        self.min_price = None
        self.max_price = None
        self.order = []
        self.where = []

    def go(self, request):
        # retrieve from cache
        #
        #
        output = None

        # cache doesn't exist, build it...
        if output is None:
            # create output dict
            output = {
                'count': {
                    'from': None,
                    'to': None,
                    'total': self.get_count(),
                },
                'pagination': None,
                'products': [],
            }

            # add products if applicable
            if output['count']['total'] > 0:
                output['products'] = self.get_list()

                # set count numbers
                output['count']['from'] = (self.offset or 0) + 1
                output['count']['to'] = output['count']['from'] + len(output['products']) - 1

                # pagination
                if self.include_pagination:
                    self.pagination['num_of_pages'] = math.ceil(output['count']['total'] / self.pagination['items_per_page'])
                    self.pagination['page_range'] = range(1, self.pagination['num_of_pages'] + 1)
                    output['pagination'] = self.pagination
                    self.pagination['has_previous'] = self.pagination['page_num'] > 1
                    if self.pagination['has_previous']:
                        self.pagination['previous'] = self.pagination['page_num'] - 1
                    self.pagination['has_next'] = self.pagination['page_num'] < self.pagination['num_of_pages']
                    if self.pagination['has_next']:
                        self.pagination['next'] = self.pagination['page_num'] + 1

                # modify content
                for p in output['products']:
                    # price
                    p['orig_price'] = price_display(p['orig_price'])
                    p['sale_price'] = price_display(p['sale_price'])

                    # rating
                    if 'rating' in p:
                        p['rating'] = get_rating_dict(p['rating'])

                    # images
                    p['p_image'] = image_path(p['p_image'])
                    p['v_image'] = image_path(p['v_image'])

        # save to cache
        #
        #

        # personalise content
        for p in output['products']:
            p['in_basket'] = str(p['v_id']) in \
                request.session['basket']['basket']['contents']
            p['in_wishlist'] = p['v_id'] in \
                request.session['basket']['wishlist']['contents']

        return output

    def get_count(self):
        sql = self.get_subquery('count')
        return fetchsinglevalue('SELECT COUNT(*) FROM (%s) AS q' % sql)

    def get_list(self):
        sql = 'SELECT * FROM (%s) AS x' % self.get_subquery('list')

        # add ordering
        self.order.append('p_name ASC')
        sql = '%s ORDER BY %s' % (sql, ', '.join(self.order))

        # set limit / offset
        if self.limit is not None:
            sql = '%s LIMIT %s' % (sql, self.limit)
        if self.offset is not None:
            sql = '%s OFFSET %s' % (sql, self.offset)

        return dictfetchall(sql)

    def get_subquery(self, action):
        sql = """
            SELECT          DISTINCT ON (pv.product_id) [FIELDS] [EXTRAS]
            FROM            saleboxdjango_productvariant AS pv
            INNER JOIN      saleboxdjango_product AS p ON p.id = pv.product_id
            [RATING_JOIN]
            [WHERE]
            ORDER BY        pv.product_id, price ASC
        """

        if action == 'count':
            sql = sql.replace('[FIELDS]', 'pv.product_id')
            sql = sql.replace('[EXTRAS]', '')

        if action == 'list':
            # fields
            fields = [
                'p.category_id',
                'p.id AS p_id',
                'p.name AS p_name',
                'p.image AS p_image',
                'p.slug AS p_slug',
                'pv.id AS v_id',
                'pv.slug AS v_slug',
                'pv.image AS v_image',
                'pv.shipping_weight AS v_shipping_weight',
                'pv.string_1 AS v_string_1',
                'pv.string_2 AS v_string_2',
                'pv.string_3 AS v_string_3',
                'pv.string_4 AS v_string_4',
                'pv.int_1 AS v_int_1',
                'pv.int_2 AS v_int_2',
                'pv.int_3 AS v_int_3',
                'pv.int_4 AS v_int_4',
                'pv.price AS orig_price'
            ]

            # sale caclulation
            if self.member_discount_active and self.member_discount_rate > 0:
                tmp = (100 - self.member_discount_rate) / 100
                fields.append('CASE pv.member_discount_applicable WHEN true THEN pv.price * %s ELSE pv.price END AS sale_price' % tmp)
            else:
                fields.append('pv.price AS sale_price')

            # rating
            if self.include_rating:
                fields.append('COALESCE(prc.rating, 0) AS rating')
                fields.append('COALESCE(prc.vote_count, 0) AS vote_count')
            sql = sql.replace('[FIELDS]', ', '.join(fields))

            # extras
            sql = sql.replace('[EXTRAS]', '')

        # rating join
        if action == 'list' and self.include_rating:
            sql = sql.replace(
                '[RATING_JOIN]',
                'LEFT JOIN saleboxdjango_productratingcache AS prc ON p.id = prc.product_id'
            )
        else:
            sql = sql.replace('[RATING_JOIN]', '')

        # where clause(s)
        sql = sql.replace('[WHERE]', self.get_where())

        return sql

    def get_where(self):
        where = self.where + [
            'pv.available_on_ecom = true',
            'pv.active_flag = true',
            'p.active_flag = true'
        ]

        # min / max price
        if self.min_price is not None:
            where.append('pv.sale_price >= %s' % self.min_price)
        if self.max_price is not None:
            where.append('pv.sale_price <= %s' % self.max_price)

        # compile sql
        return 'WHERE %s' % ' AND '.join(where)

    def set_attribute_product(self, number, attribute):
        template = 'SELECT product_id FROM saleboxdjango_product_attribute_%s WHERE attributeitem_id = %s'
        sql = template % (number, attribute.id)
        self.where.append('p.id IN (%s)' % sql)

    def set_attribute_variant(self, number, attribute):
        template = 'SELECT productvariant_id FROM saleboxdjango_productvariant_attribute_%s WHERE attributeitem_id = %s'
        sql = template % (number, attribute.id)
        self.where.append('pv.id IN (%s)' % sql)

    def set_category(self, category, include_child_categories=True):
        if include_child_categories:
            id_list = category \
                        .get_descendants(include_self=True) \
                        .values_list('id', flat=True)
        else:
            id_list = [category.id]
        id_list = ','.join([str(i) for i in id_list])

        self.where.append('p.category_id IN (%s)' % id_list)

    def set_order_preset(self, preset):
        presets = {
            'price_low_to_high': 'sale_price ASC',
            'price_high_to_low': 'sale_price DESC',
            'rating_low_to_high': 'rating ASC',
            'rating_high_to_low': 'rating DESC',
        }

        # error prevention...
        if preset.startswith('rating_'):
            self.set_include_rating()

        self.order.append(presets[preset])

    def set_price_filter(self, mn=None, mx=None):
        self.min_price = mn
        self.max_price = mx

    def set_limit_offset(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset

    def set_member_discount(self, rate):
        if rate < 0 or rate > 100:
            raise 'Invalid rate'

        self.member_discount_active = True
        self.member_discount_rate = rate

    def set_pagination(self, page_num, items_per_page, url_prefix):
        self.include_pagination = True
        self.pagination['page_num'] = page_num
        self.pagination['items_per_page'] = items_per_page
        self.pagination['url_prefix'] = url_prefix

        self.limit = items_per_page
        self.offset = (page_num - 1) * items_per_page

    def set_include_rating(self, value=True):
        self.include_rating = value


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
                'image': a.image,
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
        'image': c.image,
        'product_count': len(set(list(product_ids))),
        'slug': c.slug,
        'slug_path': c.slug_path,
        'children': [get_category_tree_recurse(c) for c in children]
    }


def translate_path(path):
    o = {}
    o['path_list'] = path.strip('/').split('/')

    try:
        o['page_num'] = int(o['path_list'][-1])
        if o['page_num'] < 1:
            raise Http404()
        o['path_list'] = o['path_list'][:-1]
        if len(o['path_list']) == 0:
            o['path_list'].append('')
    except:
        o['page_num'] = 1



    o['path'] = '/'.join(o['path_list'])
    return o
