from django.http import JsonResponse

from saleboxdjango.forms import BasketForm, RatingForm, \
    SwitchBasketWishlistForm, WishlistForm
from saleboxdjango.lib.basket import get_basket_wishlist_html, \
    set_basket, set_wishlist, switch_basket_wishlist
from saleboxdjango.models import ProductVariant, ProductVariantRating


def basket_ajax_view(request):
    if request.method == 'POST':
        form = BasketForm(request.POST)
        if form.is_valid():
            set_basket(
                request,
                ProductVariant.objects.get(id=form.cleaned_data['variant_id']),
                form.cleaned_data['quantity'],
                form.cleaned_data['relative']
            )

    return JsonResponse({
        'basketHtml': get_basket_wishlist_html(request, True, 25),
        'basketCount': request.session['basket']['count']
    })


def rating_ajax_view(request):
    if request.user.is_authenticated and request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            variant = ProductVariant \
                        .objects \
                        .get(id=form.cleaned_data['variant_id'])

            # delete
            if form.cleaned_data['rating'] == -1:
                o = ProductVariantRating \
                        .objects \
                        .filter(user=request.user) \
                        .filter(variant=variant)

                if len(o) > 0:
                    o[0].delete()

            # add
            else:
                o, created = ProductVariantRating \
                                .objects \
                                .get_or_create(user=request.user, variant=variant)

                o.rating = form.cleaned_data['rating']
                o.save()

    return JsonResponse({})


def switch_basket_wishlist_ajax_view(request):
    if request.method == 'POST':
        form = SwitchBasketWishlistForm(request.POST)
        if form.is_valid():
            switch_basket_wishlist(
                request,
                ProductVariant.objects.get(id=form.cleaned_data['variant_id']),
                form.cleaned_data['destination']
            )

    return JsonResponse({
        'basketHtml': get_basket_wishlist_html(request, True, 25),
        'basketCount': request.session['basket']['count'],
        'wishlistHtml': get_basket_wishlist_html(request, False),
    })


def wishlist_ajax_view(request):
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            set_wishlist(
                request,
                ProductVariant.objects.get(id=form.cleaned_data['variant_id']),
                form.cleaned_data['add']
            )

    return JsonResponse({
        'wishlistHtml': get_basket_wishlist_html(request, False),
    })
