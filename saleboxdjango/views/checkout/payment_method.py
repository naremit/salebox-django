from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutPaymentMethodForm(forms.Form):
    pass


class SaleboxCheckoutPaymentMethodView(SaleboxCheckoutBaseView):
    checkout_step = 'payment_method'
    form_class = SaleboxCheckoutPaymentMethodForm
    template_name = 'salebox/checkout/payment_method.html'
