from django.urls import path

from saleboxdjango.views import basket_view

urlpatterns = [
    path('basket/', basket_view)
]
