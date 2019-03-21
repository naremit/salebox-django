from django.urls import path

from .views.address.remove import SaleboxAddressRemoveView
from .views.address.set_default import SaleboxAddressSetDefaultView

from saleboxdjango.views.address.address import addresslist_ajax_view
from saleboxdjango.views.basket import basket_ajax_view, \
    switch_basket_wishlist_ajax_view, wishlist_ajax_view
from saleboxdjango.views.image import image_view
from saleboxdjango.views.rating import rating_ajax_view

urlpatterns = [
    path('address/remove/', SaleboxAddressRemoveView.as_view()),
    path('address/set-default/', SaleboxAddressSetDefaultView.as_view()),

    path('delivery-address-list/', addresslist_ajax_view),
    path('basket/', basket_ajax_view),
    path('img/<slug:imgtype>/<slug:dir>/<int:id>.<slug:hash>.<slug:suffix>', image_view),
    path('rating/', rating_ajax_view),
    path('switch-basket-wishlist/', switch_basket_wishlist_ajax_view),
    path('wishlist/', wishlist_ajax_view),
]
