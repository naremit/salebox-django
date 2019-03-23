from django.urls import path

# address
from .views.address.add import SaleboxAddressAddView
from .views.address.remove import SaleboxAddressRemoveView
from .views.address.set_default import SaleboxAddressSetDefaultView

# basket
from .views.basket.basket import SaleboxBasketBasketView
from .views.basket.migrate import SaleboxBasketMigrateView
from .views.basket.wishlist import SaleboxBasketWishlistView

# image
from saleboxdjango.views.image import image_view

# rating
from saleboxdjango.views.rating import rating_ajax_view

urlpatterns = [
    # address
    path('address/add/', SaleboxAddressAddView.as_view()),
    path('address/remove/', SaleboxAddressRemoveView.as_view()),
    path('address/set-default/', SaleboxAddressSetDefaultView.as_view()),

    # basket
    path('basket/basket/', SaleboxBasketBasketView.as_view()),
    path('basket/migrate/', SaleboxBasketMigrateView.as_view()),
    path('basket/wishlist/', SaleboxBasketWishlistView.as_view()),

    # image
    path('img/<slug:imgtype>/<slug:dir>/<int:id>.<slug:hash>.<slug:suffix>', image_view),

    # rating
    path('rating/', rating_ajax_view),
]
