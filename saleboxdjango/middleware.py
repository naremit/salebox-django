import datetime
import re

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

from saleboxdjango.lib.basket import SaleboxBasket


class SaleboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # kick out inactive (i.e. banned) users
        if request.user.is_authenticated and not request.user.is_active:
            request.session['saleboxbasket'] = None
            logout(request)
            return redirect('/')

        # init shopping basket
        sb = SaleboxBasket(request)

        # set product_list_order
        request.session.setdefault(
            'product_list_order',
            settings.SALEBOX['SESSION']['DEFAULT_PRODUCT_LIST_ORDER']
        )
        if 'product_list_order' in request.GET:
            valid_orders = [
                'bestseller_low_to_high',
                'bestseller_high_to_low',
                'price_low_to_high',
                'price_high_to_low',
                'rating_high_to_low',
                'rating_low_to_high',
            ]
            if request.GET['product_list_order'] in valid_orders:
                request.session['product_list_order'] = request.GET['product_list_order']
                if re.search(r'\d+\/$', request.path):
                    return redirect(re.sub(r'\d+\/$', '', request.path))

        # create response
        response = self.get_response(request)
        if sb.get_cookie_action(request) == 'add':
            response.set_cookie(
                'psessionid',
                value=request.session.session_key,
                max_age=60 * 60 * 24 * 365
            )
        elif sb.get_cookie_action(request) == 'remove':
            response.delete_cookie('psessionid')
        return response
