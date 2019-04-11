from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAccountAddressView(TemplateView):
    default_values = {}
    template_name = 'salebox/account/address.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.sa = SaleboxAddress(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.form = SaleboxAddressAddForm(initial=self.default_values)
        return self.output(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = SaleboxAddressAddForm(request.POST, initial=self.default_values)
        if self.form.is_valid():
            print(self.form['country'], print(self.form['country_state']))

        return self.output(request, *args, **kwargs)

    def output(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # init values
        context['addresses'] = self.sa.get()
        context['address_form'] = self.form
        context['address_extras'] = self.sa.form_extras(
            country_id=self.form['country'].value()
        )

        """
        # add address if one POSTed in
        add_status, add_address, add_form, add_state = sa.add_form(
            request,
            default_country_id=self.default_country_id
        )

        # prevent refreshing the page adding a duplicate address
        if add_status == 'success':
            return redirect(request.get_full_path())

        # update context
        # context['addresses'] = sa.render_list(sa.get_list())
        # context['add_form'] = add_form
        """
        return self.render_to_response(context)
