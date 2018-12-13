from django.db.models import Sum
from django.template.loader import render_to_string

from saleboxdjango.lib.common import image_path_option, price_display
from saleboxdjango.models import BasketWishlist


def get_basket_wishlist_html(request, basket=True, default_max_qty=20):
    context = {
        'basket_detail': get_basket_wishlist(request, basket, default_max_qty),
        'request': request
    }

    if basket:
        return render_to_string('_basket.html', context)
    else:
        return render_to_string('_wishlist.html', context)


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
            # image
            'image': image_path_option(
                b.variant.image,
                b.variant.product.image
            ),

            # prices
            'price': price_display(b.variant.price * b.quantity),

            # category
            'c_id': b.variant.product.category.id,

            # product
            'p_id': b.variant.product.id,
            'p_name': b.variant.product.name,
            'p_slug': b.variant.product.slug,

            # variant
            'v_id': b.variant.id,
            'v_name': b.variant.name,
            'v_slug': b.variant.slug,
            'v_shipping_weight': b.variant.shipping_weight,
            'string_1': b.variant.string_1,
            'string_2': b.variant.string_2,
            'string_3': b.variant.string_3,
            'string_4': b.variant.string_4,
            'int_1': b.variant.int_1,
            'int_2': b.variant.int_2,
            'int_3': b.variant.int_3,
            'int_4': b.variant.int_4,

            # basket
            'id': b.id,
            'quantity': b.quantity,
            'quantity_range': range(1, max(b.quantity, default_max_qty) + 1),
            'weight': b.weight,
        })

    # TODO
    # add sale-price stuff here

    # add price total
    total = 0
    for c in contents:
        total += c['price']['price']

    return {
        'contents': contents,
        'total': price_display(total),
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

    # update session
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

    # update session
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

    # update session
    update_basket_session(request)


def update_basket_session(request):
    data = {
        'basket': {
            'count': 0,
            'contents': {},
        },
        'wishlist': {
            'count': 0,
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
            if q.variant.id not in data['basket']:
                data['basket']['contents'][str(q.variant.id)] = q.quantity
            else:
                data['basket']['contents'][str(q.variant.id)] += q.quantity
            data['basket']['count'] += q.quantity
        else:
            if q.variant.id not in data['wishlist']:
                data['wishlist']['contents'].append(q.variant.id)

    # save to session
    data['wishlist']['count'] = len(data['wishlist']['contents'])
    request.session['basket'] = data
