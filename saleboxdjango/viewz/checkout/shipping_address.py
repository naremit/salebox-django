from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingAddressForm(forms.Form):
    pass

class SaleboxCheckoutShippingAddressView(SaleboxCheckoutBaseView):
    checkout_step = 'address'
    form_class = SaleboxCheckoutShippingAddressForm
    template_name = 'checkout/address.html'  # 'checkout/shipping_address.html'