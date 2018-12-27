from django.contrib.auth import authenticate, login, logout

from saleboxdjango.lib.basket import clean_basket_wishlist
from saleboxdjango.models import BasketWishlist


def salebox_login(request, username, password):
    # get all basket items collected as an anonymous visitor
    basket = BasketWishlist \
                .objects \
                .filter(user__isnull=True) \
                .filter(session=request.session.session_key) \
                .filter(basket_flag=True)

    # do authentication
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        request.session['basket_size'] = None

        # update basket
        for b in basket:
            b.user = user
            b.session = None
            b.save()

        # clean basket
        clean_basket_wishlist(request)
        request.session['basket'] = None

        # login success
        return True

    # login failed
    return False


def salebox_logout(request):
    logout(request)
    request.session['basket'] = None
