import time

from saleboxdjango.lib.common import get_price_display
from saleboxdjango.models import BasketWishlist


from pprint import pprint


class SaleboxBasket:
    def __init__(self, request):
        self.data = None

        # init a default value if the session variable is not set
        # load the basket into memory if it exists
        request.session.setdefault('saleboxbasket', None)
        if request.session['saleboxbasket'] is not None:
            self.data = request.session['saleboxbasket']

        # check the time hasn't expired. if it has, rebuild the
        # basket details. this is to keep shopping baskets in sync
        # for those users using more than one device
        if self.data is not None:
            if int(time.time()) - request.session['saleboxbasket']['created'] > 300:
                self.data = None

        # if the user is logged in, and their new session key does not
        # match their old one, they've just logged in: migrate their
        # anonymous basket to the known user
        key = request.session.session_key
        request.session.setdefault('saleboxprevkey', key)
        if request.user.is_authenticated and request.session['saleboxprevkey'] != key:
            self._migrate_anonymous_basket(key, request.user)
            self.data = None

        # if no data exists, create it
        if self.data is None:
            self._init_basket(request)

        pprint(self.data)


    def _init_basket(self, request):
        self.data = {
            'created': int(time.time()),
            'basket': {
                'qty': 0,
                'orig_price': 0,
                'sale_price': 0,
                'loyalty': 0,
                'order': [],
                'lookup': {}
            },
            'wishlist': {
                'qty': 0,
                'order': [],
                'lookup': {}
            }
        }

        # retrieve items from db
        qs = self._filter_basket_queryset(
            request,
            BasketWishlist.objects.all()
        )

        # populate data
        for q in qs:
            pv = {
                'default_image': q.variant.default_image,
                'ecommerce_description': q.variant.ecommerce_description,
                'id': q.variant.id,
                'image': q.variant.image,
                'int_1': q.variant.int_1,
                'int_2': q.variant.int_2,
                'int_3': q.variant.int_3,
                'int_4': q.variant.int_4,
                'local_image': q.variant.local_image,
                'loyalty_points': q.variant.loyalty_points,
                'member_discount_applicable': q.variant.member_discount_applicable,
                'name': q.variant.name,
                'plu': q.variant.plu,
                'price': q.variant.price,
                'product': q.variant.product.id,
                'rating_score': q.variant.rating_score,
                'rating_vote_count': q.variant.rating_vote_count,
                'sale_percent': q.variant.sale_percent,
                'sale_price': q.variant.sale_price,
                'shipping_weight': q.variant.shipping_weight,
                'size_uom': q.variant.size_uom,
                'sku': q.variant.sku,
                'slug': q.variant.slug,
                'string_1': q.variant.string_1,
                'string_2': q.variant.string_2,
                'string_3': q.variant.string_3,
                'string_4': q.variant.string_4,
            }

            if q.basket_flag:
                self.data['basket']['qty'] += q.quantity
                if q.variant.id not in self.data['basket']['order']:
                    self.data['basket']['order'].append(q.variant.id)
                    self.data['basket']['lookup'][q.variant.id] = {
                        'qty': q.quantity,
                        'variant': pv
                    }
                else:
                    self.data['basket']['lookup'][q.variant.id]['qty'] += q.quantity
            else:
                if q.variant.id not in self.data['wishlist']['order']:
                    self.data['wishlist']['qty'] += q.quantity
                    self.data['wishlist']['items'].append(pv)

        # calculate basket value
        #
        #

        # calculate loyalty points
        #
        #

        # display prices
        for s in ['orig_price', 'sale_price']:
            self.data['basket'][s] = get_price_display(self.data['basket'][s])

        # save to session
        request.session['saleboxbasket'] = self.data


    def _filter_basket_queryset(self, request, qs):
        qs = qs.select_related(
            'variant',
            'variant__product'
        )

        if request.user.is_authenticated:
            return qs.filter(user=request.user) \
                     .filter(session__isnull=True)
        else:
            return qs.filter(user__isnull=True) \
                     .filter(session=request.session.session_key)


    def _migrate_anonymous_basket(self, key, user):
        # get all basket items from previously anonymous visitor
        basket = BasketWishlist \
                    .objects \
                    .filter(user__isnull=True) \
                    .filter(session=key) \


        for b in basket:
            b.user = user
            b.session = None
            b.save()