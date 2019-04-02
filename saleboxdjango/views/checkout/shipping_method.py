from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingMethodForm(forms.Form):
    pass

class SaleboxCheckoutShippingMethodView(SaleboxCheckoutBaseView):
    get_shipping_options = None
    checkout_step = 'shipping_method'
    form_class = SaleboxCheckoutShippingMethodForm
    template_name = 'salebox/checkout/shipping_method.html'

    def get_additional_context_data(self, context):
        if self.get_shipping_options:
            context = self.get_shipping_options(
                self.request,
                self.sc,
                context
        )

        return context


def get_shipping_options_function(request, checkout, context):
    context['shipping_options'] = [
        {
            'provider': 'postoffice',
            'service': 'regular',
            'price': 1000,
            'id': 1
        },
        {
            'provider': 'courier',
            'service': 'regular',
            'price': 1500,
            'id': 2
        },
        {
            'provider': 'courier',
            'service': 'express',
            'price': 2000,
            'id': 3
        },
    ]
    return context