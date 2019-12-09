from django import forms
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from saleboxdjango.models import CheckoutStore
from saleboxdjango.views.callback.callback import SaleboxCallbackView


class SaleboxProvider2C2PCallbackForm(forms.Form):
    order_id = forms.CharField()
    payment_status = forms.CharField()
    user_defined_1 = forms.CharField()


@method_decorator(csrf_exempt, name='dispatch')
class SaleboxProviders2C2PCallbackView(SaleboxCallbackView):
    def post(self, request):
        form = SaleboxProvider2C2PCallbackForm(request.POST)
        if form.is_valid():
            cs = self._get_store(
                form.cleaned_data['user_defined_1'],
                form.cleaned_data['order_id']
            )

            if cs is not None:
                # WARNING: be aware 2c2p send rejections followed by successes
                if cs.status not in [30, 31]:
                    status = form.cleaned_data['payment_status']

                    # success
                    if status == '000':
                        cs.set_status(30)

                    # reject
                    if status in ['002', '003', '999']:
                        cs.set_status(40)

                # save update
                self._save_store_update(cs, cs.status, request.POST)

        # repond
        return super().post(request)
