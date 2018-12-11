import datetime

from django.conf import settings

from saleboxdjango.lib.basket import update_basket_session


class SaleboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # set basket_refresh
        now = datetime.datetime.now().timestamp()
        request.session.setdefault('basket_refresh', now)
        if now - request.session['basket_refresh'] > 300:  # 5 minutes
            request.session['basket_refresh'] = now
            update_basket_session(request)

        # set basket
        request.session.setdefault('basket', None)
        if request.session['basket'] is None:
            update_basket_session(request)

        # set product_list_order
        request.session.setdefault(
            'product_list_order',
            settings.SALEBOX['SESSION']['DEFAULT_PRODUCT_LIST_ORDER']
        )
        if 'product_list_order' in request.GET:
            valid_orders = [
                'price_low_to_high',
                'price_high_to_low',
                'rating_high_to_low',
                'rating_low_to_high',
            ]
            if request.GET['product_list_order'] in valid_orders:
                request.session['product_list_order'] = request.GET['product_list_order']

        response = self.get_response(request)
        return response
