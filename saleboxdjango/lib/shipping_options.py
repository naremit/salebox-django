from saleboxdjango.lib.common import get_price_display

class SaleboxShippingOptions:
    DEFAULT_SELECT = None  # or 'CHEAPEST', 'FIRST'
    REMOVE_UNAVAILABLE = True
    SORT_BY = None  # or 'PRICE_ASC', 'LABEL'

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

        opts = self.get_options()

        # remove nulls
        opts = [o for o in opts if o is not None]

        # optional: remove unavailable
        # you *may* want to keep unavailable options in the list but greyed out
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

        # format the price
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