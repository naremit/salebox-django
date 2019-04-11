from django import forms
from django.shortcuts import redirect

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.views.checkout.base import SaleboxCheckoutBaseView


class SaleboxCheckoutShippingInvoiceAddressForm(forms.Form):
    shipping_address_id = forms.IntegerField()
    invoice_required = forms.BooleanField(required=False)
    invoice_address_id = forms.IntegerField(required=False)


class SaleboxFormNameForm(forms.Form):
    salebox_form_name = forms.ChoiceField(choices=(
        ('select_address', 'select_address'),
        ('add_shipping', 'add_shipping'),
        ('add_invoice', 'add_invoice'),
    ))

class SaleboxCheckoutShippingInvoiceAddressView(SaleboxCheckoutBaseView):
    initial = {}
    checkout_step = 'shipping_invoice_address'
    form_class = SaleboxCheckoutShippingInvoiceAddressForm
    template_name = 'salebox/checkout/shipping_invoice_address.html'

    """
    def check_add_form(self, request):
        # add a new address if it has been POSTed in
        sa = SaleboxAddress(self.request.user)
        add_status, add_address, add_form, add_state = sa.add_form(
            request,
            default_country_id=self.default_country_id
        )

        # reload this page if address successfully added
        if add_status == 'success':
            add_address = sa.get_single_by_id(add_address.id)
            if add_state == 'shipping':
                self.set_shipping_address(add_address)
            else:
                self.set_invoice_address(add_address)

            return self.sc.get_current_page_path(self.checkout_step)

        return None

    def form_valid_pre_redirect(self, form):
        sa = SaleboxAddress(self.request.user)

        # set checkout shipping address
        shipping_address = sa.get_single_by_id(
            form.cleaned_data['shipping_address_id']
        )
        self.set_shipping_address(shipping_address)

        # set checkout invoice address
        if form.cleaned_data['invoice_required']:
            invoice_address = sa.get_single_by_id(
                form.cleaned_data['invoice_address_id']
            )
            self.set_invoice_address(invoice_address)
        else:
            self.sc.set_invoice_address(
                False,
                None,
                None,
                None,
                self.request
            )

        return True
    """

    def get(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)
        self.invoice_form = SaleboxAddressAddForm(initial=self.initial)
        return super().get(self, request, *args, **kwargs)


    def get_additional_context_data(self, context):
        sa = SaleboxAddress(self.request.user)

        # existing address lists
        context['shipping_addresses'] = sa.get(
            force_selected=True
        )
        context['invoice_addresses'] = sa.get(
            non_null_fields=['tax_id'],
            force_selected=True
        )

        # return
        context['shipping_address_extras'] = sa.form_extras(
            country_id=self.shipping_form['country'].value()
        )
        context['invoice_address_extras'] = sa.form_extras(
            country_id=self.invoice_form['country'].value()
        )
        context['shipping_address_id'] = self.sc.data['shipping_address']['id']
        context['invoice_address_id'] = self.sc.data['invoice_address']['id']
        context['invoice_required'] = self.sc.data['invoice_address']['required']
        return context

    def post(self, request, *args, **kwargs):
        self.shipping_form = SaleboxAddressAddForm(initial=self.initial)
        self.invoice_form = SaleboxAddressAddForm(initial=self.initial)

        # which action is being performed?
        form = SaleboxFormNameForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['salebox_form_name']
        else:
            return self.get(request, *args, **kwargs)

        # action: user has selected an option
        if action == 'select_address':
            pass

        # action: user is adding a shipping address
        if action == 'add_shipping':
            self.shipping_form = SaleboxAddressAddForm(
                request.POST,
                initial=self.initial
            )
            if self.shipping_form.is_valid():
                # add address to db
                # update checkout
                # redirect to self to prevent refresh
                pass

        # action: user is adding an invoice address
        if action == 'add_invoice':
            print('add invoice')
            self.invoice_form = SaleboxAddressAddForm(
                request.POST,
                initial=self.initial
            )
            if self.invoice_form.is_valid():
                tax_id = self.invoice_form.cleaned_data['tax_id']
                if tax_id is not None and len(tax_id.strip()) > 4:
                    # add address to db
                    sa = SaleboxAddress(self.request.user)
                    address = sa.add(self.invoice_form)

                    # update checkout
                    self.sc.set_invoice_address(
                        True,
                        address.id,
                        '%s, %s' % (
                            address.full_name,
                            ', '.join(address.address_list)
                        ),
                        None,
                        self.request
                    )

                    # redirect to self to prevent refresh
                    return redirect(request.get_full_path())

        # if we've reached this point, some input was invalid...
        # just re-show the page
        return self.form_invalid(form)

    """
    def get_additional_context_data(self, context):
        sa = SaleboxAddress(self.request.user)

        # init shipping
        shipping_addresses = sa.get()

        # init invoice
        invoice_addresses = sa.get(non_null_fields=['tax_id'])


        print('...')

        addresses = sa.get_list()

        # init empty shipping address form
        add_status, add_address, add_shipping_form, add_state = sa.add_form(
            self.request,
            state='shipping',
            default_country_id=self.default_country_id
        )

        # get selected shipping address from checkout dict, else use the default
        selected_shipping_address_id = self.sc.data['shipping_address']['id']
        if selected_shipping_address_id is None:
            for a in addresses:
                if a.default:
                    selected_shipping_address_id = a.id
                    break

        # init empty invoice address form
        add_status, add_address, add_invoice_form, add_state = sa.add_form(
            self.request,
            state='invoice',
            default_country_id=self.default_country_id,
            show_set_as_default=False
        )

        # get selected invoice address from checkout dict, else use the default
        selected_invoice_address_id = self.sc.data['invoice_address']['id']
        if selected_invoice_address_id is None:
            for a in addresses:
                if a.default:
                    selected_invoice_address_id = a.id
                    break

        # add to context
        context['has_addresses'] = len(addresses) > 0
        context['add_shipping_form'] = add_shipping_form
        context['add_invoice_form'] = add_invoice_form
        context['invoice_required'] = self.sc.data['invoice_address']['required']
        context['shipping_address_list'] = sa.render_list_radio(
            addresses,
            field_name='shipping_address_id',
            selected_id=selected_shipping_address_id
        )
        context['invoice_address_list'] = sa.render_list_radio(
            addresses,
            field_name='invoice_address_id',
            selected_id=selected_invoice_address_id
        )
        return context

    def post(self, request, *args, **kwargs):
        r = self.check_add_form(request)
        if r is not None:
            return redirect(r)

        # this form needs an extra step:
        # the invoice_address_id is required if invoice_required == True
        form = self.get_form()
        if form.is_valid():
            if form.cleaned_data['invoice_required'] and form.cleaned_data['invoice_address_id'] is None:
                return self.form_invalid(form)

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def set_invoice_address(self, address):
        self.sc.set_invoice_address(
            True,
            address.id,
            '%s, %s' % (
                address.full_name,
                ', '.join(address.address_list)
            ),
            None,
            self.request
        )

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
    """
