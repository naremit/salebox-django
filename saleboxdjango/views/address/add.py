from saleboxdjango.views.address.base import SaleboxAddressView
from saleboxdjango.forms import SaleboxAddressAddForm

from saleboxdjango.models import UserAddress


class SaleboxAddressAddView(SaleboxAddressView):
    action = 'address-add'
    form = SaleboxAddressAddForm

    def form_valid(self, request):
        try:
            ua = UserAddress(
                user=request.user,
                default=form.cleaned_data['set_default'],
                address_group=form.cleaned_data['address_group'] or 'default',

            )
            ua.save()
            self.status = 'success'
        except:
            self.status = 'fail'

