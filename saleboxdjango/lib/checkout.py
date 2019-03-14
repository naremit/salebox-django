import time
from pprint import pprint

from django.conf import settings


class SaleboxCheckout:
    def __init__(self, request):
        #self.data = {'basket': []}
        #self._write_session(request)

        self._init_sequence()
        self._init_session(request)
        self._write_session(request)


    def get_checkout_nav(self, curr_page_name):
        nav = {}
        for s in self.sequence['order']:
            nav[s] = {
                'accessible': self.sequence['lookup'][s]['accessible'],
                'current': s == curr_page_name
            }
        return nav


    def get_raw_data(self):
        return self.data


    def get_last_accessible_page(self):
        for o in reversed(self.sequence['order']):
            if self.sequence['lookup'][o]['accessible']:
                return self.sequence['lookup'][o]['path']

        return None


    def get_next_page(self, page_name):
        next = self.sequence['order'].index(page_name) + 1
        if next < len(self.sequence['order']):
            return self.sequence['lookup'][
                self.sequence['order'][next]
            ]['path']
        else:
            return None


    def page_redirect(self, page_name):
        if page_name not in self.sequence['order']:
            raise Exception('Unrecognised SaleboxCheckout page_name: ' % page_name)

        # if basket empty, redirect to the pre-checkout page, e.g.
        # typically the shopping basket
        if len(self.data['basket']) == 0:
            return settings.SALEBOX['CHECKOUT']['PRE_URL']

        # if this page is not marked accessible, i.e. the user is
        # trying to jump steps in the process, redirect them to
        # the 'last known good' page
        if not self.is_page_accessible(page_name):
            return self.get_last_accessible_page()

        return None


    def is_page_accessible(self, page_name):
        try:
            return self.sequence['lookup'][page_name]['accessible']
        except:
            return False


    def set_basket(self, basket, request, reset_completed=True, reset_checkout=True):
        self.data['basket'] = basket.get_raw_data()
        if reset_completed:
            self.data['completed'] = []
        self._write_session(request)
        return self.sequence['lookup'][
            self.sequence['order'][0]
        ]['path']


    def set_completed(self, page_name, request):
        self.data['completed'].append(page_name)
        self._update_sequence()
        self._write_session(request)
        return self.get_next_page(page_name)


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

        # update data
        self._update_sequence()
        self.data['last_seen'] = int(time.time())


    def _update_sequence(self):
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