from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from saleboxdjango.lib.address import SaleboxAddress
from saleboxdjango.models import UserAddress


class SaleboxAccountAddressView(TemplateView):
    default_country_id = None
    language = None
    template_name = 'salebox/account/address.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.output(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.output(request, *args, **kwargs)

    def output(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        # init address class
        sa = SaleboxAddress(request.user)

        # add address if one POSTed in
        add_status, add_address, add_form, add_state = sa.add_form(
            request,
            lang=self.language,
            default_country_id=self.default_country_id
        )

        # prevent refreshing the page adding a duplicate address
        if add_status == 'success':
            return redirect(request.get_full_path())

        # update context
        context['addresses'] = sa.render_list(sa.get_list(lang=self.language))
        context['add_form'] = add_form
        return self.render_to_response(context)


class SaleboxAccountHomeView(TemplateView):
    template_name = 'salebox/account/home.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        sa = SaleboxAddress(request.user)
        context['delivery_address_count'] = sa.get_count()

        return self.render_to_response(context)
