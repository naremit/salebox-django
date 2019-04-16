from django.conf import settings

from python2c2p.redirectapi import twoctwop_redirectapi

from saleboxdjango.lib.basket import SaleboxBasket
from saleboxdjango.views.checkout.gateway import SaleboxCheckoutGatewayView


class SaleboxProviders2C2PCallbackView(SaleboxCheckoutGatewayView):
    gateway_code = '2c2p'

    def gateway(self, request, *args, **kwargs):
        context = self.get_context_data()
        store = self.sc.save_to_store(request.user, gateway_code=self.gateway_code)

        # override start
        data = self.sc.get_raw_data()

        # show all available types
        tctp = this.gateway_init(data, request)

        # reset basket  TODO - should the basket be reset on first callback?
        basket = SaleboxBasket(request)
        basket.reset_basket(request)

        # render
        context['html'] = tctp.request()
        return self.render_to_response(context)

    def gateway_init(self, data, request):
        """
        Optionally override this method if there are different
        payment parameters you wish to send
        """

        tctp = twoctwop_redirectapi(
            settings.TWOCTWOP_1['MERCHANT_ID'],
            settings.TWOCTWOP_1['SECRET_KEY'],
            settings.TWOCTWOP_1['GATEWAY_URL'],
        )
        tctp.set_value('payment_option', 'A')

        # total price
        total_price = data['basket']['sale_price'] + data['shipping_method']['price']

        # default values
        tctp.set_value('amount', total_price)
        tctp.set_value('currency', 'THB')
        tctp.set_value('customer_email', request.user.email)
        tctp.set_value('default_lang', 'th')
        tctp.set_value('order_id', store.visible_id)
        tctp.set_value('payment_description', settings.TWOCTWOP_2['PAYMENT_DESCRIPTION'])
        tctp.set_value('result_url_1', settings.TWOCTWOP_2['CALLBACK_URL_FRONTEND'],)
        tctp.set_value('result_url_2', settings.TWOCTWOP_2['CALLBACK_URL_BACKEND'],)
        tctp.set_value('user_defined_1', store.uuid)

        return tctp
