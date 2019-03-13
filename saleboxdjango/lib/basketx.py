import time

from saleboxdjango.lib.common import get_price_display
from saleboxdjango.models import BasketWishlist, ProductVariant


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
            request.session['saleboxprevkey'] = key
            self.data = None

        # if no data exists, create it
        if self.data is None:
            self._init_basket(request)

        # from pprint import pprint
        # pprint(self.data)

    def switch_basket_wishlist(self, request, variant, destination):
        if isinstance(variant, int):
            variant = ProductVariant.objects.get(id=variant)

        if destination in ['basket', 'wishlist']:
            bwl = self._filter_basket_queryset(
                request,
                BasketWishlist \
                    .objects \
                    .filter(variant=variant) \
                    .filter(basket_flag=(destination == 'wishlist'))
            )

            for b in bwl:
                b.basket_flag = (destination == 'basket')
                b.quantity = 1
                b.save()

            # re-populate basket
            self._init_basket(request)

    def update_basket(self, request, variant, qty, relative):
        if isinstance(variant, int):
            variant = ProductVariant.objects.get(id=variant)

        # get existing items to update
        items = self._get_variants(request, variant)

        # update db
        if items['basket'] is None:
            if items['wishlist'] is None:
                # create basket item
                if int(qty) > 0:
                    self._add_variant(request, variant, qty, True)
            else:
                # wishlist item exists, convert to basket
                items['wishlist'].basket_flag = True
                items['wishlist'].quantity = int(qty)
                items['wishlist'].save()
        else:
            # update basket item
            if relative:
                items['basket'].quantity += int(qty)
                if items['basket'].quantity > 0:
                    items['basket'].save()
                else:
                    items['basket'].delete()

            # delete wishlist item if exists
            if items['wishlist'] is not None:
                items['wishlist'].delete()

        # re-populate basket
        self._init_basket(request)

    def update_wishlist(self, request, variant, add):
        if isinstance(variant, int):
            variant = ProductVariant.objects.get(id=variant)

        # get existing items to update
        items = self._get_variants(request, variant)

        # update db
        if add:
            if items['wishlist'] is None:
                # add to wishlist
                self._add_variant(request, variant, 1, False)
        else:
            if items['wishlist'] is not None:
                items['wishlist'].delete()

        # re-populate basket
        self._init_basket(request)

    def _add_variant(self, request, variant, qty, basket):
        bwl = BasketWishlist(
            variant=variant,
            quantity=int(qty),
            basket_flag=True,
        )
        if request.user.is_authenticated:
            bwl.user = request.user
        else:
            bwl.session = request.session.session_key
        bwl.save()

    def _filter_basket_queryset(self, request, qs):
        qs = qs.select_related(
            'variant',
            'variant__product',
            'variant__product__category',
        )

        if request.user.is_authenticated:
            return qs.filter(user=request.user) \
                     .filter(session__isnull=True)
        else:
            return qs.filter(user__isnull=True) \
                     .filter(session=request.session.session_key)

    def _get_variants(self, request, variant):
        if isinstance(variant, int):
            variant = ProductVariant.objects.get(id=variant)

        basket = self._filter_basket_queryset(
            request,
            BasketWishlist \
                .objects \
                .filter(basket_flag=True) \
                .filter(variant=variant)
        )

        wishlist = self._filter_basket_queryset(
            request,
            BasketWishlist \
                .objects \
                .filter(basket_flag=False) \
                .filter(variant=variant)
        )

        return {
            'basket': basket.first(),
            'wishlist': wishlist.first(),
        }

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

        # clean up data
        basket_duplicates = {}

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
                'price_display': q.variant.price_display(),
                'product': {
                    'category': {
                        'id': q.variant.product.category.id,
                        'name': q.variant.product.category.name,
                        'short_name': q.variant.product.category.short_name,
                    },
                    'id': q.variant.product.id,
                    'image': q.variant.product.image,
                    'local_image': q.variant.product.local_image,
                    'name': q.variant.product.name,
                    'slug': q.variant.product.slug,
                    'sold_by': q.variant.product.sold_by,
                    'string_1': q.variant.product.string_1,
                    'string_2': q.variant.product.string_2,
                    'string_3': q.variant.product.string_3,
                    'string_4': q.variant.product.string_4,
                    'vat_applicable': q.variant.product.vat_applicable,
                },
                'rating_score': q.variant.rating_score,
                'rating_vote_count': q.variant.rating_vote_count,
                'sale_percent': q.variant.sale_percent,
                'sale_price': q.variant.sale_price,
                'sale_price_display': q.variant.sale_price_display(),
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

                if str(q.variant.id) not in basket_duplicates:
                    basket_duplicates[str(q.variant.id)] = {
                        'original': q,
                        'copies': []
                    }

                if q.variant.id not in self.data['basket']['order']:
                    self.data['basket']['order'].append(str(q.variant.id))
                    self.data['basket']['lookup'][str(q.variant.id)] = {
                        'qty': q.quantity,
                        'variant': pv
                    }
                else:
                    self.data['basket']['lookup'][q.variant.id]['qty'] += q.quantity
                    basket_duplicates[str(q.variant.id)]['copies'].append(q)
            else:
                if q.variant.id not in self.data['wishlist']['order']:
                    self.data['wishlist']['qty'] += q.quantity
                    self.data['wishlist']['order'].append(str(q.variant.id))
                    self.data['wishlist']['lookup'][str(q.variant.id)] = pv
                else:
                    q.delete()

        # cleanup
        delete_ids = []
        for d in basket_duplicates:
            for c in basket_duplicates[d]['copies']:
                basket_duplicates[d]['original'].quantity += c.quantity
                delete_ids.append(c.id)
                basket_duplicates[d]['original'].save()

        if len(delete_ids) > 0:
            BasketWishlist.objects.filter(id__in=delete_ids).delete()

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