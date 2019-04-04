from saleboxdjango.lib.binpack import BinPack
from saleboxdjango.lib.common import get_price_display


class SaleboxShippingOptions:
    DEFAULT_SELECT = None  # or 'CHEAPEST', 'FIRST'
    REMOVE_UNAVAILABLE = True
    SORT_BY = None  # or 'PRICE_ASC', 'LABEL'

    # variant variable names
    SHIPPING_WIDTH = 'int_1'
    SHIPPING_HEIGHT = 'int_2'
    SHIPPING_DEPTH = 'int_3'
    SHIPPING_WEIGHT = 'shipping_weight'

    def get_options(self):
        # This is the function you need to replace.
        # Add your own functions here, e.g.
        #
        #   return [
        #     self._example_option_1(),
        #     self._example_option_2(),
        #   ]
        #
        # Useful vars:
        #   self.checkout['shipping_address']['address']['country']
        #   self.checkout['shipping_address']['address']['country_state']
        #
        return [
            self._example_option_1(),
            self._example_option_2(),
        ]

    def go(self, request, checkout, context):
        self.request = request
        self.checkout = checkout
        self.context = context

        # get packages into a handy list for bin packing
        self.meta = {
            'total_items': 0,
            'total_weight': 0,
            'items': []
        }
        for b in checkout['basket']['basket']['items']:
            for i in range(0, b['qty']):
                self.meta['total_items'] += 1
                self.meta['total_weight'] += b['variant'][self.SHIPPING_WEIGHT] or 0
                self.meta['items'].append({
                    'variant_id': b['variant']['id'],
                    'width': b['variant'][self.SHIPPING_WIDTH],
                    'height': b['variant'][self.SHIPPING_HEIGHT],
                    'depth': b['variant'][self.SHIPPING_DEPTH],
                    'weight': b['variant'][self.SHIPPING_WEIGHT],
                })

        # build options
        opts = self.get_options()

        # remove nulls
        # if an shipping option is not available, simply return None. However...
        opts = [o for o in opts if o is not None]

        # optional: remove unavailable
        # you *may* want to keep unavailable options in the list but greyed out,
        # in which case, return the dict with ['available'] = False
        if self.REMOVE_UNAVAILABLE:
            opts = [o for o in opts if o['available'] == True]

        # optional: sorting
        if self.SORT_BY == 'PRICE_ASC':
            # todo
            pass
        if self.SORT_BY == 'LABEL':
            # todo
            pass

        # optional: default select
        if self.DEFAULT_SELECT is not None:
            # todo
            pass

        # format each option's price
        for o in opts:
            o['price'] = get_price_display(o['price'])

        # return
        self.context['shipping_options'] = opts
        return self.context

    def init_option(
            self,
            id,
            label,
            remarks,
            service,
            extras=None
        ):
        return {
            'available': True,
            'extras': extras,
            'id': id,
            'label': {
                'label': label,  # e.g. 'Post Office'
                'remarks': remarks,  # e.g. '2-3 days'
                'service': service  # 'ExpressPost'
            },
            'price': 0
        }

    def _do_binpack(self, containers, packages):
        # containers like:
        # [
        #   ['name', price, width, height, depth],
        #   ['name', price, width, height, depth],
        # ]
        bp = BinPack()

        # add containers
        for c in containers:
            bp.add_bin(c[0], c[1], c[2], c[3], c[4])

        # add packages
        for p in packages:
            bp.add_package(
                p['variant_id'],
                p['width'],
                p['height'],
                p['depth'],
            )

        return bp.go()

    def _example_option_1(self):
        method = self.init_option(
            1,
            'Post Office',
            '2-4 days',
            'Surface mail'
        )

        method['price'] = 10000
        return method

    def _example_option_2(self):
        method = self.init_option(
            2,
            'Post Office',
            '1 day',
            'NextDay'
        )

        method['price'] = 25000
        return method
