from django import forms

from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingAddressForm(forms.Form):
    shipping_address_id = forms.IntegerField()

class SaleboxCheckoutShippingAddressView(SaleboxCheckoutBaseView):
    language = None
    checkout_step = 'shipping_address'
    form_class = SaleboxCheckoutShippingAddressForm
    template_name = 'salebox/checkout/shipping_address.html'

    def form_valid_pre_redirect(self, form):
        sa = SaleboxAddress(self.request.user)
        address = sa.get_single_by_id(form.cleaned_data['shipping_address_id'])
        self.sc.set_shipping_address(
            True,
            address.id,
            None,
            None,
            self.request
        )

    def get_additional_context_data(self, context):
        sa = SaleboxAddress(self.request.user, lang=self.language)
        addresses = sa.get_list()

        # get selected address from checkout dict, else use the default
        selected_address_id = self.sc.data['shipping_address']['address_id']
        if selected_address_id is None:
            for a in addresses:
                if a.default:
                    selected_address_id = a.id
                    break

        context['address_list'] = sa.render_list_radio(
            addresses,
            field_name='shipping_address_id',
            selected_id=selected_address_id
        )

        context['has_addresses'] = len(addresses) > 0
        return context
