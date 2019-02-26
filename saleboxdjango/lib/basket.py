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

    # construct output
    if 'html_button' in results and variant_id:
        output['html_button'] = render_to_string(
            'salebox/product_list_button.html',
            {
                'pv': {
                    'id': variant_id,
                    'basket_qty': basket_wishlist['qty_variant'].get(variant_id, 0)
                },
                'request': request
            }
        )

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

    if 'loyalty' in results:
        output['loyalty'] = basket_wishlist['loyalty']

    if 'price' in results:
        output['price'] = basket_wishlist['price']

    if 'qty_total' in results:
        output['qty_total'] = basket_wishlist['qty_total']

    if 'qty_variant' in results and variant_id:
        output['qty_variant'] = basket_wishlist['qty_variant'].get(variant_id, 0)

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


def set_basket(request, variant, qty, relative):
    # ensure no duplicates
    clean_basket_wishlist(request)

    # remove corresponding wishlist item
    w = BasketWishlist \
            .objects \
            .filter(variant=variant) \
            .filter(basket_flag=False)
    w = basket_auth_filter(request, w)
    w.delete()

    # find if item already exists
    b = BasketWishlist \
            .objects \
            .filter(variant=variant) \
            .filter(basket_flag=True)
    b = basket_auth_filter(request, b)

    # update existing / create new
    if len(b) > 0:
        b = b[0]
        if relative:
            b.quantity += qty
        else:
            b.quantity = qty
    else:
        b = BasketWishlist(
            variant=variant,
            quantity=qty,
            basket_flag=True
        )
        if request.user.is_authenticated:
            b.user = request.user
        else:
            b.session = request.session.session_key

    # save / delete
    b.save()
    if b.quantity < 1:
        b.delete()

    # remove empties, update session
    clean_basket_wishlist(request)
    update_basket_session(request)


def set_wishlist(request, variant, add):
    # ensure no duplicates
    clean_basket_wishlist(request)

    # find if item already exists
    w = BasketWishlist \
            .objects \
            .filter(variant=variant) \
            .filter(basket_flag=False)
    w = basket_auth_filter(request, w)

    try:
        w = w[0]
    except:
        w = None

    # do add
    if add:
        if w is None:
            b = BasketWishlist(
                variant=variant,
                quantity=1,
                basket_flag=False
            )
            if request.user.is_authenticated:
                b.user = request.user
            else:
                b.session = request.session.session_key
            b.save()
        else:
            b.quantity = 1
            b.save()

    # do delete
    if not add and w is not None:
        w.delete()

    # remove empties, update session
    clean_basket_wishlist(request)
    update_basket_session(request)


def clean_basket_wishlist(request):
    basket = {}
    wishlist = {}

    # get contents
    contents = basket_auth_filter(
        request,
        BasketWishlist.objects.all()
    )
    contents = contents.select_related(
        'variant',
        'variant__product'
    )

    # loop through to flatten
    for i, c in enumerate(contents):
        if c.variant.product.sold_by == 'item':
            # 'merge' duplicate basket items
            if c.basket_flag:
                if c.variant.id in basket:
                    contents[basket[c.variant.id]].quantity += c.quantity
                    contents[basket[c.variant.id]].save()
                    c.quantity = 0
                    c.save()
                else:
                    basket[c.variant.id] = i

            # 'merge' duplicate wishlist items
            if not c.basket_flag:
                if c.variant.id in wishlist:
                    c.quantity = 0
                    c.save()
                else:
                    c.quantity = 1
                    c.save()
                    wishlist[c.variant.id] = i

    # delete the empty items
    BasketWishlist  \
        .objects \
        .filter(quantity__lte=0) \
        .delete()


def basket_auth_filter(request, qs):
    if request.user.is_authenticated:
        return qs.filter(user=request.user) \
                 .filter(session__isnull=True)
    else:
        return qs.filter(user__isnull=True) \
                 .filter(session=request.session.session_key)


def switch_basket_wishlist(request, variant, destination):
    # ensure no duplicates
    clean_basket_wishlist(request)

    if destination in ['basket', 'wishlist']:
        # get basket entry
        b = BasketWishlist \
                .objects \
                .filter(variant=variant) \
                .filter(basket_flag=True if destination == 'wishlist' else False)
        b = basket_auth_filter(request, b)

        # switch it
        if len(b) > 0:
            b[0].basket_flag = True if destination == 'basket' else False
            if not b[0].basket_flag:
                b[0].quantity = 1
            b[0].save()

    # remove empties, update session
    clean_basket_wishlist(request)
    update_basket_session(request)


def update_basket_session(request):
    data = {
        'basket': {
            'quantity': 0,
            'loyalty': 0,
            'price': 0,
            'contents': {},
        },
        'wishlist': {
            'quantity': 0,
            'contents': [],
        }
    }

    # retrieve from db
    qs = basket_auth_filter(
        request,
        BasketWishlist.objects.all()
    )

    # populate data
    for q in qs:
        if q.basket_flag:
            try:
                data['basket']['loyalty'] += q.quantity * q.variant.loyalty_points
            except:
                pass

            try:
                data['basket']['price'] += q.quantity * q.variant.price
            except:
                pass

            if q.variant.id not in data['basket']['contents']:
                data['basket']['contents'][str(q.variant.id)] = q.quantity
            else:
                data['basket']['contents'][str(q.variant.id)] += q.quantity
            data['basket']['quantity'] += q.quantity
        else:
            if q.variant.id not in data['wishlist']:
                data['wishlist']['contents'].append(q.variant.id)

    # save to session
    data['basket']['price'] = get_price_display(data['basket']['price'])
    data['wishlist']['quantity'] = len(data['wishlist']['contents'])
    request.session['basket'] = data
