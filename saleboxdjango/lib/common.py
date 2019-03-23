from django.conf import settings
from django.db import connection


def dictfetchall(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]


def fetchflatlist(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return [row[0] for row in cursor.fetchall()]


def fetchsinglevalue(sql):
    return fetchflatlist(sql)[0]


def get_price_display(price):
    formatted = '{:,.2f}'.format(price / 100)
    unformatted = '{:.2f}'.format(price / 100)
    minor = formatted.split('.')[1]

    return {
        'price': price,
        'float': price / 100,
        'major': int(unformatted.split('.')[0]),
        'minor': minor,
        'formatted': formatted,
        'unformatted': unformatted,
        'formatted_html': '%s<span>.%s</span>' % (formatted.split('.')[0], minor),
        'unformatted_html': '%s<span>.%s</span>' % (unformatted.split('.')[0], minor)
    }


def get_rating_display(score, vote_count):
        if vote_count > 0:
            return {
                '100': score,
                '5': round(score / 20),
                '10': round(score / 10)
            }
        else:
            return {'100': 0, '5': 0, '10': 0}


def get_sibling_variants(variant, order_by=None):
    pv = ProductVariant \
            .objects \
            .filter(active_flag=True) \
            .filter(available_on_ecom=True) \
            .filter(product__active_flag=True) \
            .filter(product__category__active_flag=True) \
            .filter(product=variant.product) \
            .annotate(selected_variant=Case(
                When(id=variant.id, then=True),
                default=Value(False),
                output_field=BooleanField(),
            ))

    if order_by is not None:
        pv = pv.order_by(order_by)

    return pv
