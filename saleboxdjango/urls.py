from django.urls import path

from saleboxdjango.views import basket_ajax_view, \
    rating_ajax_view, wishlist_ajax_view

urlpatterns = [
    path('basket/', basket_ajax_view),
    path('rating/', rating_ajax_view),
    path('wishlist/', wishlist_ajax_view),
]
