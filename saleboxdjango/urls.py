from django.urls import path

from saleboxdjango.views.address import addresslist_ajax_view
from saleboxdjango.views.basket import basket_ajax_view, \
    switch_basket_wishlist_ajax_view, wishlist_ajax_view
from saleboxdjango.views.image import image_view
from saleboxdjango.views.rating import rating_ajax_view

urlpatterns = [
    path('delivery-address-list/', addresslist_ajax_view),
    path('basket/', basket_ajax_view),
    path('img/<slug:imgtype>/<slug:dir>/<int:id>.<slug:hash>.<slug:suffix>', image_view),
    path('rating/', rating_ajax_view),
    path('switch-basket-wishlist/', switch_basket_wishlist_ajax_view),
    path('wishlist/', wishlist_ajax_view),
]
