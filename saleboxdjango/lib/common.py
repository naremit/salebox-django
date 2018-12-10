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


def price_display(price):
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
        'formatted_html': '%s.<span>%s</span>' % (formatted.split('.')[0], minor),
        'unformatted_html': '%s.<span>%s</span>' % (unformatted.split('.')[0], minor)
    }


def image_path(img):
    if img is not None:
        img = '%s%s' % (
            settings.SALEBOX['IMG']['POSASSETS'],
            img
        )

    return img


def get_rating_dict(rating):
    return {
        'rating': rating if rating else None,
        'rating_5': round(rating / 20) if rating else None,
        'rating_10': round(rating / 10) if rating else None,
    }
