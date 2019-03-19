from django.http import JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.forms import BasketForm, \
    SwitchBasketWishlistForm, WishlistForm
from saleboxdjango.lib.basket import SaleboxBasket
from saleboxdjango.models import ProductVariant


def basket_ajax_view(request):
    sb = SaleboxBasket(request)

    results = ''
    if request.method == 'POST':
        form = BasketForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['results']
            sb.update_basket(
                request,
                form.cleaned_data['variant_id'],
                form.cleaned_data['quantity'],
                form.cleaned_data['relative']
            )

    return JsonResponse(
        sb.get_data(
            request,
            results,
            form.cleaned_data['variant_id']
        )
    )


def switch_basket_wishlist_ajax_view(request):
    sb = SaleboxBasket(request)

    if request.method == 'POST':
        form = SwitchBasketWishlistForm(request.POST)
        if form.is_valid():
            sb.switch_basket_wishlist(
                request,
                form.cleaned_data['variant_id'],
                form.cleaned_data['destination']
            )

    return JsonResponse(
        sb.get_data(
            request,
            'all'
        )
    )


def wishlist_ajax_view(request):
    sb = SaleboxBasket(request)

    results = ''
    if request.method == 'POST':
        form = WishlistForm(request.POST)
        if form.is_valid():
            results = form.cleaned_data['results']
            sb.update_wishlist(
                request,
                form.cleaned_data['variant_id'],
                form.cleaned_data['add']
            )

    return JsonResponse(
        sb.get_data(
            request,
            results
        )
    )