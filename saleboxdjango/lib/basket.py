"""
from django.db.models import Sum
from django.template.loader import render_to_string

from saleboxdjango.lib.common import get_price_display
from saleboxdjango.models import BasketWishlist


def get_basket_wishlist_html(request, template, basket_wishlist):
    return render_to_string(template, {
        'basket_detail': basket_wishlist,
        'request': request
    })


def get_basket_wishlist_results(request, results, basket=True, variant_id=None):
    default_max_qty = 25  # TODO: make this a setting
    basket_wishlist = get_basket_wishlist(request, basket, default_max_qty)
    results = results.split(',')
    output = {}

    if 'html_full' in results:
        if basket:
            template = 'salebox/basket_full.html'
        else:
            template = 'salebox/wishlist_full.html'
        output['html_full'] = get_basket_wishlist_html(
            request,
            template,
            basket_wishlist
        )

    if 'html_summary' in results:
        if basket:
            template = 'salebox/basket_summary.html'
        else:
            template = 'salebox/wishlist_summary.html'
        output['html_summary'] = get_basket_wishlist_html(
            request,
            template,
            basket_wishlist
        )

    # return
    return output


def get_basket_wishlist(request, basket=True, default_max_qty=20):
    qs = basket_auth_filter(
        request,
        BasketWishlist \
            .objects \
            .filter(basket_flag=basket) \
            .order_by('variant__product__name', 'variant__name') \
            .select_related(
                'variant',
                'variant__product',
                'variant__product__category'
            )
    )

    contents = []
    for b in qs:
        contents.append({
            # basket
            'id': b.id,
            'quantity': b.quantity,
            'quantity_range': range(1, max(b.quantity, default_max_qty) + 1),
            'weight': b.weight,

            # product detail
            'category': b.variant.product.category,
            'product': b.variant.product,
            'variant': b.variant,

            # image
            'image': b.variant.default_image,

            # prices
            'price': get_price_display(b.variant.sale_price * b.quantity),
        })

    # add price total
    qty_total = 0
    qty_variant = {}
    loyalty = 0
    price = 0
    for c in contents:
        qty_total += c['quantity']
        qty_variant[c['variant'].id] = c['quantity']
        try:
            loyalty += c['quantity'] * c['variant'].loyalty_points
        except:
            pass
        price += c['price']['price']

    return {
        'contents': contents,
        'loyalty': loyalty,
        'price': get_price_display(price),
        'qty_total': qty_total,
        'qty_variant': qty_variant,
    }
"""