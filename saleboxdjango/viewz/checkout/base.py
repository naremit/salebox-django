from django.conf import settings
from django.shortcuts import redirect
from django.views.generic import FormView

from saleboxdjango.lib.checkout import SaleboxCheckout


class SaleboxCheckoutBaseView(FormView):
    checkout_step = None


    def get_conf(self, name, default):
        return settings.SALEBOX['CHECKOUT'].get(name, default)


    def dispatch(self, request, *args, **kwargs):
        # friendlier error messages
        if self.checkout_step is None:
            raise Exception('You need to define a checkout_step')
        if self.form_class is None:
            raise Exception('You need to define a form_class')

        # get defaults
        user_must_be_authenticated = self.get_conf(
            'CHECKOUT_USER_MUST_BE_AUTHENTICATED',
            True
        )
        user_not_authenticated_redirect = self.get_conf(
            'CHECKOUT_USER_NOT_AUTHENTICATED_REDIRECT',
            '/'
        )

        # check logged in
        if user_must_be_authenticated and not request.user.is_authenticated:
            return redirect(user_not_authenticated_redirect)

        # get checkout object
        self.sc = SaleboxCheckout(request)
        r = self.sc.page_redirect(self.checkout_step)
        if r is not None:
            return redirect(r)

        # default dispatch action
        return super().dispatch(request, *args, **kwargs)


    def form_valid(self, form, request):
        # add your custom code here
        # once complete, you will probably want to run...
        # return super().form_valid(self, form, request)
        # ...to run the code below

        # set as complete and redirect to the next step
        r = self.sc.set_completed(self.checkout_step, request)
        return redirect(r)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['checkout'] = {
            'data': self.sc.get_raw_data(),
            'nav': self.sc.get_checkout_nav(self.checkout_step),
            'step': self.checkout_step
        }
        return context


    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form, request)
        else:
            return self.form_invalid(form)