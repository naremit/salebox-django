from opposablethumbs.opposablethumbs import OpposableThumbs

from django.conf import settings
from django.http import Http404, JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.forms import BasketForm, RatingForm, \
    SwitchBasketWishlistForm, WishlistForm
from saleboxdjango.lib.basket import get_basket_wishlist_results, \
    set_basket, set_wishlist, switch_basket_wishlist
from saleboxdjango.models import ProductVariant, ProductVariantRating, UserAddress


def addresslist_ajax_view(request):
    if request.method == 'POST':
        try:
            address = UserAddress \
                        .objects \
                        .filter(user=request.user) \
                        .filter(address_type='d') \
                        .filter(id=int(request.POST['address_id']))[0]

            action = request.POST['action']

            if action == 'remove':
                address.delete()

            if action == 'set_default':
                address.default = True
                address.save()
        except:
            pass

    context = {
        'addresses': UserAddress.objects.filter(user=request.user).filter(address_type='d')
    }

    return JsonResponse({
        'addressHtml': render_to_string('salebox/address_list.html', context)
    })


def basket_ajax_view(request):
    results = ''
    if request.method == 'POST':
        form = BasketForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['results']
            set_basket(
                request,
                ProductVariant.objects.get(id=form.cleaned_data['variant_id']),
                form.cleaned_data['quantity'],
                form.cleaned_data['relative']
            )

    return JsonResponse(
        get_basket_wishlist_results(
            request,
            results,
            True,
            form.cleaned_data['variant_id']
        )
    )


def image_view(request, imgtype, dir, id, hash, suffix):
    try:
        f = '%s/salebox/%s/%s.%s.%s' % (
            settings.MEDIA_ROOT,
            dir,
            id,
            hash,
            suffix
        )
        params = 'file=%s&%s' % (f, settings.SALEBOX['IMG'][imgtype])
        ot = OpposableThumbs(params)
        return ot.response()
    except:
        raise Http404()


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
                        .filter(variant=variant) \
                        .first()

                if o is not None:
                    o.delete()

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
        'basket': get_basket_wishlist_html(request, True, 25),
        'wishlist': get_basket_wishlist_html(request, False),
    })


def wishlist_ajax_view(request):
    results = ''
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['results']
            set_wishlist(
                request,
                ProductVariant.objects.get(id=form.cleaned_data['variant_id']),
                form.cleaned_data['add']
            )

    return JsonResponse(get_basket_wishlist_results(request, results, False))
