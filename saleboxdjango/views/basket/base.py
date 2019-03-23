from saleboxdjango.views.base import SaleboxBaseView
from saleboxdjango.lib.basket import SaleboxBasket


class SaleboxBasketView(SaleboxBaseView):
    def init_class(self, request):
        self.sb = SaleboxBasket(request)
