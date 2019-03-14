import time
from pprint import pprint

from django.conf import settings


class SaleboxCheckout:
    def __init__(self, request):
        self._init_sequence()
        self._init_session(request)
        self._write_session(request)


    def page_accessible(self, page_name):
        if page_name not in self.sequence['order']:
            raise Exception('Unrecognised SaleboxCheckout page_name: ' % page_name)

        # if basket empty, redirect to the pre-checkout page, e.g.
        # typically the shopping basket
        if len(self.data['basket']) == 0:
            return settings.SALEBOX['CHECKOUT']['PRE_URL']

        # if this page is not marked accessible, i.e. the user is
        # trying to jump steps in the process, redirect them to
        # the 'last known good' page
        if not self.sequence['lookup'][page_name]['accessible']:
            for o in reversed(self.sequence['order']):
                if self.sequence['lookup'][o]['accessible']:
                    return self.sequence['lookup'][o]['path']

        # user has access to this page...
        return None


    def set_basket(self, basket):
        self.data['basket'] = basket
        self._write_session()


    def _init_sequence(self):
        self.sequence = {
            'order': [],
            'lookup': {}
        }

        for i, s in enumerate(settings.SALEBOX['CHECKOUT']['SEQUENCE']):
            self.sequence['order'].append(s[0])
            self.sequence['lookup'][s[0]] = {
                'path': s[1],
                'position': i,
                'complete': False,
                'accessible': i == 0
            }


    def _init_session(self, request):
        # create empty values
        self.data = {
            'basket': {},
            'completed': [],
            'data': {},
        }
        request.session.setdefault('saleboxcheckout', None)

        # attempt to import data from the session
        if request.session['saleboxcheckout'] is not None:
            tmp = request.session['saleboxcheckout']
            if int(time.time()) - tmp['last_seen'] < 60 * 60:  # 1 hr
                self.data = request.session['saleboxcheckout']

        # update sequence
        for i, o in enumerate(self.sequence['order']):
            if o in self.data['completed']:
                self.sequence['lookup'][o]['complete'] = True
                self.sequence['lookup'][o]['accessible'] = True
                try:
                    self.sequence['lookup'][
                        self.sequence['order'][i + 1]
                    ]['accessible'] = True
                except:
                    pass

        # update last_seen value
        self.data['last_seen'] = int(time.time())


    def _write_session(self, request):
        if len(self.data['basket']) == 0:
            request.session['saleboxcheckout'] = None
        else:
            request.session['saleboxcheckout'] = self.data






"""
init...

- take the checkout sequence from settings:
  - CHECKOUT_INIT_URL: /basket/  <-- url to redirect to if we don't have a checkout dict
  - CHECKOUT_SEQUENCE: [
      code: e.g. shipping_method
      url: /checkout/shipping/
      complete: False  <-- you can only see a this page if it is the first page, or the one before it is marked complete
  ]

- is there a checkout dict in the session?
  - is it old? delete it
  - is it fresh? import it


- dict {
    last_seen: 1132131312,
    basket: {...},
    completed: []
}
"""