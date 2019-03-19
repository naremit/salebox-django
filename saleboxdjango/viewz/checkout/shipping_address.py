from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingAddressForm(forms.Form):
    pass

class SaleboxCheckoutShippingAddressView(SaleboxCheckoutBaseView):
    checkout_step = 'shipping_address'
    form_class = SaleboxCheckoutShippingAddressForm
    template_name = 'salebox/checkout/shipping_address.html'