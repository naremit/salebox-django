from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingMethodForm(forms.Form):
    pass

class SaleboxCheckoutShippingMethodView(SaleboxCheckoutBaseView):
    checkout_step = 'shipping_method'
    form_class = SaleboxCheckoutShippingMethodForm
    template_name = 'salebox/checkout/shipping_method.html'