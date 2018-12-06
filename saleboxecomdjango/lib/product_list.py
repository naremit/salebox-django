from saleboxecomdjango.lib.common import fetchsinglevalue
from saleboxecomdjango.models import Product, ProductRatingCache


class ProductList:
    offset = None
    limit = None
    min_orig_price = None
    max_orig_price = None

    def __init__(self):
        pass

    def go(self):
        output = {
            'count': fetchsinglevalue(self.get_sql('count')),
            'products': []
        }

        if output['count'] > 0:
            output['products'] = Product.objects.raw(self.get_sql('list'))

        return output

    def get_sql(self, action):
        sql = """
            SELECT              [ACTION]
            FROM                saleboxecomdjango_product AS p
            [RATING_JOIN]
            [WHERE]
            [ORDER_BY]
            [LIMIT]
            [OFFSET]
        """

        # add where clause(s)
        sql = sql.replace('[WHERE]', self.get_where())

        # action: count
        if action == 'count':
            sql = sql.replace('[ACTION]', 'COUNT(*)')
            sql = sql.replace('[RATING_JOIN]', '')
            sql = sql.replace('[LIMIT]', '')
            sql = sql.replace('[OFFSET]', '')

        # action: list
        if action == 'list':
            sql = sql.replace('[ACTION]', '*, prc.vote_count, prc.score')
            sql = sql.replace('[RATING_JOIN]', 'LEFT JOIN saleboxecomdjango_productratingcache AS prc ON p.id = prc.product_id')
            sql = sql.replace('[LIMIT]', 'LIMIT %s' % self.limit if self.limit else '')
            sql = sql.replace('[OFFSET]', 'OFFSET %s' % self.offset if self.offset else '')

        # order by
        sql = sql.replace('[ORDER_BY]', '')

        print(sql)
        return sql

    def get_where(self):
        where = []

        # orig price
        if self.max_orig_price is not None:
            where.append(
                self.get_where_price_range(
                    'max_orig',
                    self.max_orig_price
                )
            )
        if self.min_orig_price is not None:
            where.append(
                self.get_where_price_range(
                    'min_orig',
                    self.min_orig_price
                )
            )

        if len(where) > 0:
            return 'WHERE %s' % ' AND '.join(where)
        else:
            return ''

    def get_where_price_range(self, field, value):
        sql = """
            p.id IN (
                SELECT      DISTINCT(product_id)
                FROM        saleboxecomdjango_productvariant
                WHERE       [FIELD] [COMPARISON] %s
            )
        """ % value

        if field.endswith('_orig'):
            sql = sql.replace('[FIELD]', 'price')
        if field.startswith('min_'):
            sql = sql.replace('[COMPARISON]', '>=')
        else:
            sql = sql.replace('[COMPARISON]', '<=')

        return sql

    def set_orig_price_filter(self, mn=None, mx=None):
        self.min_orig_price = mn
        self.max_orig_price = mx

    def set_limit_offset(self, limit=None, offset=None):
        self.limit = limit
        self.offset = offset
