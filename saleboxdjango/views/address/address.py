from django.http import JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.models import UserAddress


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
        'addresses': UserAddress \
                        .objects \
                        .filter(user=request.user) \
                        .filter(address_type='d')
    }

    return JsonResponse({
        'addressHtml': render_to_string('salebox/address_list.html', context)
    })