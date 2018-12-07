from saleboxdjango.lib.basket import get_basket_size


class SaleboxMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # set basket_size
        request.session.setdefault('basket_size', None)
        if request.session['basket_size'] is None:
            request.session['basket_size'] = get_basket_size(request)

        # set product_list_order
        request.session.setdefault('product_list_order', 'rating_high_to_low')
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
