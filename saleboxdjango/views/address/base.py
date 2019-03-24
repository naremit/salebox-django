from saleboxdjango.views.base import SaleboxBaseView
from saleboxdjango.lib.address import SaleboxAddress


class SaleboxAddressView(SaleboxBaseView):
    language = None

    def init_class(self, request):
        self.sa = SaleboxAddress(request.user, lang=self.language)
