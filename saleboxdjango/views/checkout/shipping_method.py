from django import forms

from saleboxdjango.lib.shipping_options import SaleboxShippingOptions
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingMethodForm(forms.Form):
    pass

class SaleboxCheckoutShippingMethodView(SaleboxCheckoutBaseView):
    shipping_options_class = SaleboxShippingOptions
    checkout_step = 'shipping_method'
    form_class = SaleboxCheckoutShippingMethodForm
    template_name = 'salebox/checkout/shipping_method.html'

    def get_additional_context_data(self, context):
        smc = self.shipping_options_class()
        return smc.go(
            self.request,
            self.sc.get_raw_data(),
            context
        )