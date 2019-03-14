import time

from django.template.loader import render_to_string

from saleboxdjango.lib.common import get_price_display
from saleboxdjango.models import BasketWishlist, ProductVariant


class SaleboxBasket:
    def __init__(self, request):
        self.cookie = None
        self.data = None

        # init a default value if the session variable is not set
        # load the basket into memory if it exists
        request.session.setdefault('saleboxbasket', None)
        if request.session['saleboxbasket'] is not None:
            self.data = request.session['saleboxbasket']

        # if the user is not logged in, store their sessionid in a cookie
        # so we can use it later to fetch their anonymous basket
        key = request.session.session_key
        if not request.user.is_authenticated:
            if key is None:
                # just logged out, clear any lingering data
                self.data = None
            else:
                try:
                    if request.COOKIES['psessionid'] != key:
                        self.cookie = 'add'
                except:
                    self.cookie = 'add'

        # if the user is logged in, see if their sessionid has changed.
        # if so, they've just logged in and we need to migrate their
        # anonymous basket to their user one
        if request.user.is_authenticated:
            try:
                if request.COOKIES['psessionid'] != key:
                    self._migrate_anonymous_basket(
                        request.COOKIES['psessionid'],
                        request.user
                    )
                    self.cookie = 'remove'
                    self.data = None
            except:
                pass

        # check the time hasn't expired. if it has, rebuild the
        # basket details. this is to keep shopping baskets in sync
        # for those users using more than one device
        if self.data is not None:
            if int(time.time()) - request.session['saleboxbasket']['created'] > 300:
                self.data = None

        # if no data exists, create it
        if self.data is None:
            self._init_basket(request)


    def get_cookie_action(self, request):
        return self.cookie


    def get_data(self, request, results, variant_id=None):
        results = results.split(',')
        o = {}

        # construct output
        if 'all' in results:
            results = [
                'basket_html_button',
                'basket_html_full',
                'basket_html_summary',
                'basket_loyalty',
                'basket_price',
                'basket_qty_total',
                'basket_qty_variant',
                'wishlist_html_button',
                'wishlist_html_full',
                'wishlist_html_summary',
            ]

        if 'basket_html_button' in results and variant_id:
            try:
                qty = self.data['basket']['lookup'][str(variant_id)]['qty']
            except:
                qty = 0

            o['basket_html_button'] = render_to_string(
                'salebox/product_list_button.html',
                {
                    'pv': {
                        'id': variant_id,
                        'basket_qty': qty
                    },
                    'request': request
                },
                request
            )

        if 'basket_html_full' in results:
            o['basket_html_full'] = render_to_string(
                'salebox/basket_full.html',
                {
                    'data': self.data,
                    'request': request
                },
                request
            )

        if 'basket_html_summary' in results:
            """
            TODO
            o['basket_html_summary'] = render_to_string(
                'salebox/basket_summary.html', {
                    'data': self.data,
                    'request': request
                }
            )
            """
            pass

        if 'basket_loyalty' in results:
            o['basket_loyalty'] = self.data['basket']['loyalty']

        if 'basket_price' in results:
            o['basket_price'] = {
                'orig_price': self.data['basket']['orig_price'],
                'sale_price': self.data['basket']['sale_price']
            }

        if 'basket_qty_total' in results:
            o['basket_qty_total'] = self.data['basket']['qty']

        if 'basket_qty_variant' in results and variant_id:
            o['basket_qty_variant'] = len(self.data['basket']['order'])

        if 'wishlist_html_button' in results and variant_id:
            # todo - add/remove from wishlist button
            #
            #
            pass

        if 'wishlist_html_full' in results:
            o['wishlist_html_full'] = render_to_string(
                'salebox/wishlist_full.html', {
                    'data': self.data,
                    'request': request
                },
                request
            )

        if 'wishlist_html_summary' in results:
            """
            TODO
            o['wishlist_html_summary'] = render_to_string(
                'salebox/wishlist_summary.html', {
                    'data': self.data,
                    'request': request
                }
            )
            """
            pass

        return o


    def get_raw_data(self):
        return self.data


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
            else:
                items['basket'].quantity = int(qty)
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


    def _calculate_loyalty(self):
        for i in self.data['basket']['items']:
            if i['variant']['loyalty_points'] is not None:
                self.data['basket']['loyalty'] += i['variant']['loyalty_points'] * i['qty']


    def _calculate_price(self):
        for i in self.data['basket']['items']:
            i['variant']['qty_price'] = get_price_display(i['variant']['price'] * i['qty'])
            i['variant']['qty_sale_price'] = get_price_display(i['variant']['sale_price'] * i['qty'])
            self.data['basket']['orig_price'] += i['variant']['price'] * i['qty']
            self.data['basket']['sale_price'] += i['variant']['sale_price'] * i['qty']


    def _filter_basket_queryset(self, request, qs):
        qs = qs.select_related(
            'variant',
            'variant__product',
            'variant__product__category',
        )
        qs = qs.order_by('created')

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
                'items': [],
                'order': [],
                'lookup': {}
            },
            'wishlist': {
                'qty': 0,
                'order': [],
                'items': [],
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

        # populate the items list
        for i in self.data['basket']['order']:
            self.data['basket']['items'].append(self.data['basket']['lookup'][str(i)])
        for i in self.data['wishlist']['order']:
            self.data['wishlist']['items'].append(self.data['wishlist']['lookup'][str(i)])

        # cleanup
        delete_ids = []
        for d in basket_duplicates:
            for c in basket_duplicates[d]['copies']:
                delete_ids.append(c.id)
                basket_duplicates[d]['original'].quantity += c.quantity
                basket_duplicates[d]['original'].save()

        if len(delete_ids) > 0:
            BasketWishlist.objects.filter(id__in=delete_ids).delete()

        # calculate basket value + loyalty points
        self._calculate_price()
        self._calculate_loyalty()

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