import datetime

from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect

from saleboxdjango.lib.basket import update_basket_session


class SaleboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # kick out inactive users
        if request.user.is_authenticated and not request.user.is_active:
            request.session['basket'] = None
            logout(request)
            redirect('/')

        # set basket_refresh (update the user's basket every 5 minutes -
        # used to reflect changes they may have made on a different device)
        now = datetime.datetime.now().timestamp()
        request.session.setdefault('basket_refresh', now)
        if now - request.session['basket_refresh'] > 300:  # 5 minutes
            request.session['basket_refresh'] = now
            update_basket_session(request)

        # set basket
        request.session.setdefault('basket', None)
        if request.session['basket'] is None:
            update_basket_session(request)

        # if the user is not logged in, store their session_id in the session
        # so we can populate their cart on login
        if not request.user.is_authenticated:
            key = request.session.session_key
            if key is not None:
                if 'prev_session_key' in request.session:
                    if request.session['prev_session_key'] != key:
                        request.session['prev_session_key'] = key
                else:
                    request.session['prev_session_key'] = key

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

        response = self.get_response(request)
        return response
