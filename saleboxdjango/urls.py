from django.urls import path

from .views.address.add import SaleboxAddressAddView
from .views.address.remove import SaleboxAddressRemoveView
from .views.address.set_default import SaleboxAddressSetDefaultView

from .views.basket.basket import SaleboxBasketBasketView
# from .views.basket.migrate import SaleboxBasketMigrateView
# from .views.basket.wishlist import SaleboxBasketWishlistView

#from saleboxdjango.views.basket import basket_ajax_view, \
#    switch_basket_wishlist_ajax_view, wishlist_ajax_view
from saleboxdjango.views.image import image_view
from saleboxdjango.views.rating import rating_ajax_view

urlpatterns = [
    path('address/add/', SaleboxAddressAddView.as_view()),
    path('address/remove/', SaleboxAddressRemoveView.as_view()),
    path('address/set-default/', SaleboxAddressSetDefaultView.as_view()),

    path('basket/basket/', SaleboxBasketBasketView.as_view()),
    # path('basket/migrate/', SaleboxBasketMigrateView.as_view()),
    # path('basket/wishlist/', SaleboxBasketWishlistView.as_view()),

    # path('basket/', basket_ajax_view),
    # path('switch-basket-wishlist/', switch_basket_wishlist_ajax_view),
    # path('wishlist/', wishlist_ajax_view),

    path('img/<slug:imgtype>/<slug:dir>/<int:id>.<slug:hash>.<slug:suffix>', image_view),

    path('rating/', rating_ajax_view),
]
