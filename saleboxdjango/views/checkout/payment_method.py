from django import forms
from .base import SaleboxCheckoutBaseView


class SaleboxCheckoutPaymentMethodForm(forms.Form):
    payment_method = forms.ChoiceField(choices=(
        ('card', 'Credit or Debit Card'),
        ('wallet', 'E-Wallet'),
    ))


class SaleboxCheckoutPaymentMethodView(SaleboxCheckoutBaseView):
    checkout_step = 'payment_method'
    form_class = SaleboxCheckoutPaymentMethodForm
    template_name = 'salebox/checkout/payment_method.html'

    def form_valid_pre_redirect(self, form):
        method = form.cleaned_data['payment_method']
        self.sc.set_payment_method(method, None, self.request)
        return True
