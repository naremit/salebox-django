from django.http import JsonResponse

from saleboxdjango.forms import BasketForm
from saleboxdjango.lib.basket import add_basket_item


def basket_view(request):
    if request.method == 'POST':
        form = BasketForm(request.POST)
        if form.is_valid():
            print('ok')

    return JsonResponse({})
