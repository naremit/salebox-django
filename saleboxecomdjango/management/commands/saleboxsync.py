import datetime
import requests
from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from saleboxecomdjango.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        do_sync = True
        while do_sync:
            do_sync = self.do_sync()

    def do_sync(self):
        post = {
            'pos': settings.SALEBOX['API']['KEY'],
            'license': settings.SALEBOX['API']['LICENSE'],
            'platform_type': 'ECOMMERCE',
            'platform_version': '0.1.6',
        }

        # populate last updates
        sync_from_dict = self.get_sync_from_dict()
        for code in sync_from_dict:
            post['lu_%s' % code] = sync_from_dict[code]

        pprint(sync_from_dict)

        # do request
        url = '%s/api/pos/v2/sync' % settings.SALEBOX['API']['URL']
        r = requests.post(url, data=post)

        # handle response
        try:
            response = r.json()
            if response['status'] == 'OK':
                for i, value in enumerate(response['sync']):
                    if value['code'] == 'attribute':
                        self.sync_attribute(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'attribute_item':
                        self.sync_attribute_item(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'discount_seasonal_group':
                        self.sync_discount_seasonal_group(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'discount_seasonal_ruleset':
                        self.sync_discount_seasonal_ruleset(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'member':
                        self.sync_member(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'member_group':
                        self.sync_member_group(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product':
                        self.sync_product(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product_category':
                        self.sync_product_category(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product_variant':
                        self.sync_product_variant(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    else:
                        print('Error: %s' % value['code'])

                return response['resync_now']
                # return False
        except:
            return False

    def get_sync_from_dict(self):
        lus = LastUpdate.objects.all()

        # populate dict
        lu = {}
        for l in lus:
            lu[l.code] = l.value

        # fill in the gaps
        for code in [
            'attribute',
            'attribute_item',
            'discount_seasonal_group',
            'discount_seasonal_ruleset',
            'member',
            'member_group',
            'product',
            'product_category',
            'product_variant',
        ]:
            if code not in lu:
                LastUpdate(code=code, value=0.0).save()
                lu[code] = 0.0

        return lu

    def set_sync_from_dict(self, code, increment, sync_from_dict, api_lu):
        if increment:
            now = datetime.datetime.utcnow().timestamp()
            if now - api_lu > 60:
                if api_lu == 0:
                    api_lu = 1.0
                else:
                    api_lu += 0.000001

        if api_lu > sync_from_dict[code]:
            lu = LastUpdate.objects.get(code=code)
            lu.value = float(api_lu)
            lu.save()

    def sync_attribute(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'attribute',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_attribute_item(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'attribute_item',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_discount_seasonal_group(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'discount_seasonal_group',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_discount_seasonal_ruleset(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'discount_seasonal_ruleset',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_member(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'member',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_member_group(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'member_group',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_product(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'product',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )

    def sync_product_category(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'product_category',
            True,
            sync_from_dict,
            api_lu
        )

    def sync_product_variant(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        self.set_sync_from_dict(
            'product_variant',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )
