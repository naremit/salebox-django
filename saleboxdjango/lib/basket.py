from django.db.models import Sum
from saleboxdjango.models import BasketWishlist


def get_basket_size(self, request):
    qs = BasketWishlist.objects.filter(basket_flag=True)
    if request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    else:
        qs = qs.filter(session=request.session.session_key)
    return qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
