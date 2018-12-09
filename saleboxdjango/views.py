from django.http import JsonResponse

from saleboxdjango.forms import BasketForm, WishlistForm
from saleboxdjango.lib.basket import set_basket, set_wishlist
from saleboxdjango.models import ProductVariant


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
        'count': request.session['basket']['count']
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

    return JsonResponse({})
