from django.db.models import Sum

from saleboxdjango.models import BasketWishlist


def add_basket_item(request, variant, qty=1):
    # ensure no duplicates
    clean_basket_wishlist(request)

    # find if item already exists
    b = BasketWishlist \
            .objects \
            .filter(variant=variant) \
            .filter(basket_flag=True)
    b = basket_auth_filter(request, b)

    # update existing / create new
    if len(b) > 0:
        b[0].quantity += qty
        b[0].save()
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
        b.save()

    # update count
    request.session['basket_size'] = get_basket_size(request)


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
    BasketWishlist.objects.filter(quantity__lte=0).delete()


def basket_auth_filter(request, qs):
    if request.user.is_authenticated:
        return qs.filter(user=request.user) \
                 .filter(session__isnull=True)
    else:
        return qs.filter(user__isnull=True) \
                 .filter(session=request.session.session_key)


def set_basket_session(request):
    data = {
        'count': 0,
        'basket': {},
        'wishlist': [],
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
                data['basket'][q.variant.id] = q.quantity
            else:
                data['basket'][q.variant.id] += q.quantity
            data['count'] += q.quantity
        else:
            if q.variant.id not in data['wishlist']:
                data['wishlist'].append(q.variant.id)

    # save to session
    request.session['basket'] = data
