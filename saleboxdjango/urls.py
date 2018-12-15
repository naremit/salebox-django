from django.urls import path

from saleboxdjango.views import *

urlpatterns = [
    path('delivery-address-list/', addresslist_ajax_view),
    path('basket/', basket_ajax_view),
    path('rating/', rating_ajax_view),
    path('switch-basket-wishlist/', switch_basket_wishlist_ajax_view),
    path('wishlist/', wishlist_ajax_view),
]
