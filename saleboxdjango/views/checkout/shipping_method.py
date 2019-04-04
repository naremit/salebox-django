from django import forms

from saleboxdjango.lib.shipping_options import SaleboxShippingOptions
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingMethodForm(forms.Form):
    shipping_method = forms.IntegerField()

class SaleboxCheckoutShippingMethodView(SaleboxCheckoutBaseView):
    shipping_options_class = SaleboxShippingOptions
    checkout_step = 'shipping_method'
    form_class = SaleboxCheckoutShippingMethodForm
    template_name = 'salebox/checkout/shipping_method.html'

    def get_additional_context_data(self, context):
        return self._get_shipping_options(context)

    def form_valid_pre_redirect(self, form):
        # retrieve selected option
        id = form.cleaned_data['shipping_method']
        options = self._get_shipping_options()['shipping_options']
        selected = next(o for o in options if o['id'] == id)

        # store in checkout
        self.sc.set_shipping_method(
            selected['id'],
            selected['price']['price'],
            selected['extras'],
            self.request
        )

    def _get_shipping_options(self, context={}):
        smc = self.shipping_options_class()
        return smc.go(
            self.request,
            self.sc.get_raw_data(),
            context
        )
