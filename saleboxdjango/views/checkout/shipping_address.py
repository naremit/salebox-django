from django import forms
from django.shortcuts import redirect

from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingAddressForm(forms.Form):
    shipping_address_id = forms.IntegerField()


class SaleboxCheckoutShippingAddressView(SaleboxCheckoutBaseView):
    language = None
    default_country_id = None
    checkout_step = 'shipping_address'
    form_class = SaleboxCheckoutShippingAddressForm
    template_name = 'salebox/checkout/shipping_address.html'

    def check_add_form(self, request):
        # add a new address if it has been posted in
        sa = SaleboxAddress(self.request.user, lang=self.language)
        add_status, add_address, add_form, add_state = sa.add_form(
            request,
            default_country_id=self.default_country_id
        )

        # redirect to next page if address successfully added, else
        # continue as normal
        if add_status == 'success':
            add_address = sa.get_single_by_id(add_address.id)
            self.set_shipping_address(add_address)
            return self.sc.set_completed(self.checkout_step, request)
        else:
            self.add_form = add_form
            self.add_status = add_status
            return None

    def form_valid_pre_redirect(self, form):
        sa = SaleboxAddress(self.request.user)
        address = sa.get_single_by_id(form.cleaned_data['shipping_address_id'])
        self.set_shipping_address(address)

    def get(self, request, *args, **kwargs):
        self.check_add_form(request)
        return super().get(self, request, *args, **kwargs)

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

        # add to context
        context['has_addresses'] = len(addresses) > 0
        context['add_form'] = self.add_form
        context['add_status'] = self.add_status
        context['address_list'] = sa.render_list_radio(
            addresses,
            field_name='shipping_address_id',
            selected_id=selected_address_id
        )
        return context

    def post(self, request, *args, **kwargs):
        r = self.check_add_form(request)
        if r is not None:
            return redirect(r)
        return super().post(self, request, *args, **kwargs)

    def set_shipping_address(self, address):
        self.sc.set_shipping_address(
            True,
            address.id,
            '%s, %s' % (
                address.full_name,
                ', '.join(address.address_list)
            ),
            None,
            self.request
        )
