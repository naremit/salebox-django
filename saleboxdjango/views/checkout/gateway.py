from django import forms
from django.conf import settings
from django.shortcuts import redirect

from .base import SaleboxCheckoutBaseView
from saleboxdjango.lib.basket import SaleboxBasket
from saleboxdjango.models import ProductVariant


class SaleboxCheckoutGatewayForm(forms.Form):
    pass


class SaleboxCheckoutGatewayView(SaleboxCheckoutBaseView):
    http_method_names = ['get', 'post']

    checkout_step = 'gateway'
    form_class = SaleboxCheckoutGatewayForm
    template_name = 'salebox/checkout/gateway.html'

    def gateway(self, request, *args, **kwargs):
        context = self.get_context_data()
        store = self.sc.save_to_store(request.user)

        # override this middle section relevant to your needs
        #
        #
        #
        context['html'] = '<form><!-- PUT YOUR CODE HERE --></form>'

        # reset the shopping basket
        basket = SaleboxBasket(request)
        basket.reset_basket(request)

        # render the gateway redirect
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        return self.validate(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.validate(request, *args, **kwargs)

    def validate(self, request, *args, **kwargs):
        # check everything in the basket is in stock
        if not self.validate_stock():
            # there is not enough stock available to
            # fulfil this customer's order...

            # force the basket data to be rebuilt
            request.session['saleboxbasket']['created'] = 0

            # redirect to the basket page. in future we should add
            # some messaging to the customer here too
            return redirect(settings.SALEBOX['CHECKOUT']['PRE_URL'])

        # check discounts (e.g. codes) are still valid
        if not self.validate_discounts():
            # something is wrong with the discount applied to this order,
            # i.e it is no longer valid somehow

            # todo
            # undo the problem here
            #
            #

            # redirect to the basket page. in future we should add
            # some messaging to the customer here too
            return redirect(settings.SALEBOX['CHECKOUT']['PRE_URL'])

        # everything ok, proceed to payment gateway
        return self.gateway(request, *args, **kwargs)

    def validate_discounts(self):
        # todo
        #
        #

        return True

    def validate_stock(self):
        data = self.sc.get_raw_data()

        # create dict of variant_id / qty
        basket = {}
        for item in data['basket']['items']:
            if item['variant']['id'] not in basket:
                basket[item['variant']['id']] = 0
            basket[item['variant']['id']] += item['qty']

        # ignore non-inventory basket items
        non_inventory_ids = ProductVariant \
                                .objects \
                                .filter(id__in=list(basket.keys())) \
                                .filter(product__inventory_type__in=['I', 'C']) \
                                .values_list('id', flat=True)
        for id in non_inventory_ids:
            del basket[id]

        # return False if there are more items in the basket
        # than there are available in stock
        variants = ProductVariant \
                    .objects \
                    .filter(id__in=list(basket.keys())) \
                    .filter(preorder_flag=False)
        for pv in variants:
            if pv.stock_total < basket[pv.id]:
                return False

        return True