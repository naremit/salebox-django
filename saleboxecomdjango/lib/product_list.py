from saleboxecomdjango.lib.common import fetchsinglevalue, dictfetchall
from saleboxecomdjango.models import Product, ProductRatingCache


class ProductList:
    def __init__(self):
        self.include_rating = False
        self.offset = None
        self.limit = None
        self.min_orig_price = None
        self.max_orig_price = None
        self.min_sale_price = None
        self.max_sale_price = None

    def go(self):
        self.include_rating = True

        # create output dict
        output = {
            'count': self.get_count(),
            'products': [],
        }

        # add products if applicable
        if output['count'] > 0:
            output['products'] = self.get_list()

        return output

    def get_count(self):
        sql = self.get_subquery('count')
        return fetchsinglevalue('SELECT COUNT(*) FROM (%s) AS q' % sql)

    def get_list(self):
        sql = self.get_subquery('list')

        # set limit / offset
        if self.limit is not None:
            sql = '%s LIMIT %s' % (sql, self.limit)
        if self.offset is not None:
            sql = '%s LIMIT %s' % (sql, self.offset)

        # ...
        print(sql)
        return dictfetchall(sql)

    def get_subquery(self, action):
        sql = """
            SELECT          DISTINCT ON (pv.product_id) [FIELDS] [EXTRAS]
            FROM            saleboxecomdjango_productvariant AS pv
            INNER JOIN      saleboxecomdjango_product AS p ON p.id = pv.product_id
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
                'LEFT JOIN saleboxecomdjango_productratingcache AS prc ON p.id = prc.product_id'
            )
        else:
            sql = sql.replace('[RATING_JOIN]', '')

        # where clause(s)
        sql = sql.replace('[WHERE]', self.get_where())

        return sql

    def get_where(self):
        where = [
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

    def set_orig_price_filter(self, mn=None, mx=None):
        self.min_orig_price = mn
        self.max_orig_price = mx

    def set_limit_offset(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset
