import math
from django.conf import settings
from saleboxdjango.lib.common import fetchsinglevalue, dictfetchall
from saleboxdjango.models import Product, ProductRatingCache


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

        self.include_rating = False
        self.offset = None
        self.limit = None
        self.min_orig_price = None
        self.max_orig_price = None
        self.min_sale_price = None
        self.max_sale_price = None
        self.order = []
        self.where = []

    def go(self):
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
                p['price_float'] = p['price'] / 100
                minor, major = math.modf(p['price_float'])
                p['price_major'] = int(major)
                p['price_minor'] = int(minor)
                p['price_minor_str'] = ('00%s' % p['price_minor'])[-2:]

                # score
                if 'score' in p:
                    p['score_10'] = math.floor(p['score'] / 10)
                    p['score_5'] = math.floor(p['score'] / 20)

                # images
                if p['p_image'] is not None:
                    p['p_image'] = '%s%s' % (settings.SALEBOX['IMG']['POSASSETS'], p['p_image'])
                if p['v_image'] is not None:
                    p['v_image'] = '%s%s' % (settings.SALEBOX['IMG']['POSASSETS'], p['v_image'])

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
                'pv.price AS price',
            ]
            if self.include_rating:
                fields.append('COALESCE(prc.score, 0) AS score')
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

        # min / max orig price
        if self.min_orig_price is not None:
            where.append('pv.price >= %s' % self.min_orig_price)
        if self.max_orig_price is not None:
            where.append('pv.price <= %s' % self.max_orig_price)

        # compile sql
        return 'WHERE %s' % ' AND '.join(where)

    def set_category(self, category, include_child_categories=False):
        self.where.append('p.category_id = %s' % category.id)

    def set_order_preset(self, preset):
        presets = {
            'price_low_to_high': 'price ASC',
            'price_high_to_low': 'price DESC',
            'rating_low_to_high': 'score ASC',
            'rating_high_to_low': 'score DESC',
        }

        # error prevention...
        if preset.startswith('rating_'):
            self.set_include_rating()

        self.order.append(presets[preset])

    def set_orig_price_filter(self, mn=None, mx=None):
        self.min_orig_price = mn
        self.max_orig_price = mx

    def set_limit_offset(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset

    def set_pagination(self, page_num, items_per_page, url_prefix):
        self.include_pagination = True
        self.pagination['page_num'] = page_num
        self.pagination['items_per_page'] = items_per_page
        self.pagination['url_prefix'] = url_prefix

        self.limit = items_per_page
        self.offset = (page_num - 1) * items_per_page

    def set_include_rating(self, value=True):
        self.include_rating = value
