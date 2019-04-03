class SaleboxShippingOptions:
    SORT_BY = 'DO_NOT_SORT'  # or 'PRICE_ASC', 'LABEL'
    REMOVE_UNAVAILABLE = True

    def get_options(self):
        # This is the function you need to replace.
        # Add your own functions here, e.g.
        #
        #   return [
        #     self._postoffice(),
        #     self._courier(),
        #   ]
        #
        # Useful vars:
        #   checkout['shipping_address']['address']['country']
        #   checkout['shipping_address']['address']['country_state']
        #
        return [
            self._example_option_1(),
            self._example_option_2(),
        ]

    def go(self, request, checkout, context):
        opts = self.get_options()

        # remove None
        opts = [o for o in opts if o is not None]

        # optional: remove unavailable
        if self.REMOVE_UNAVAILABLE:
            opts = [o for o in opts if o['available'] == True]

        # optional: sort by price
        #
        #

        # optional: sort by label
        #
        #

        # return
        context['shipping_options'] = opts
        return context

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