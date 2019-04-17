import datetime
import json
import os
import requests
import time
from pprint import pprint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from saleboxdjango.lib.common import update_natural_sort
from saleboxdjango.models import *


class Command(BaseCommand):
    SOFTWARE_VERSION = '0.1.6'

    def handle(self, *args, **options):
        now = time.time()

        # bail out in sync already running
        sync_start = int(self.timer_get('saleboxsync_sync_start'))
        if (time.time() - sync_start) < 120:
            print('sync in progress: bailing out!')
            return

        # step #1: if a user needs to be converted to a member, queue it
        self.timer_set('saleboxsync_sync_start', time.time())
        user_equals_member = settings.SALEBOX['MEMBER']['USER_EQUALS_MEMBER']
        if user_equals_member != 'MANUAL':
            # 'ALWAYS': every website user should be a salebox member
            if user_equals_member == 'ALWAYS':
                user_ids = get_user_model() \
                            .objects \
                            .filter(salebox_member_id__isnull=True) \
                            .values_list('id', flat=True)

            # 'PURCHASE': every website user that makes a purchase should
            # be a salebox member
            if user_equals_member == 'PURCHASE':
                user_ids = CheckoutStore \
                            .objects \
                            .filter(status__lte=30) \
                            .filter(user__isnull=False) \
                            .values_list('user', flat=True)
                if len(user_ids) > 0:
                    user_ids = get_user_model() \
                                .objects \
                                .filter(id__in=user_ids) \
                                .filter(salebox_member_id__isnull=True) \
                                .values_list('id', flat=True)

            # give those users a salebox_member_id and details to sync
            if len(user_ids) > 0:
                users = get_user_model().objects.filter(id__in=user_ids)
                for u in users:
                    u.create_salebox_member_id()
                    u.set_salebox_member_sync('email', u.email)
                    # potential TODO:
                    # have a list of key mappings in the config
                    # which automatically get added to the sync
                    # JSON at this point

        # step #2: push users with member updates
        self.push_members()

        # step #3: pull data
        # members must be up-to-date before POSTing transactions
        pull_start = int(self.timer_get('saleboxsync_pull_start'))
        pull_start = 0
        if (time.time() - pull_start) > 599:
            while True:
                self.timer_set('saleboxsync_sync_start', time.time())
                self.timer_set('saleboxsync_pull_start', time.time())
                pull_result = self.pull()
                if pull_result:
                    print()
                    print('sleeping...')
                    print()
                    time.sleep(5)
                else:
                    break

            # pull images
            print()
            print('Downloading images...')
            print()
            self.pull_images()

        # step 4: POST transactions
        self.push_transactions()

        # finished: reset the clock
        self.timer_set('saleboxsync_sync_start', 0.0)
        print('Finished in %.3fs' % (time.time() - now))

    def init_post(self):
        return {
            'pos': settings.SALEBOX['API']['KEY'],
            'license': settings.SALEBOX['API']['LICENSE'],
            'platform_type': 'ECOMMERCE',
            'platform_version': self.SOFTWARE_VERSION
        }

    def pull(self):
        post = self.init_post()

        # populate last updates
        sync_from_dict = self.pull_get_sync_from_dict()
        for code in sync_from_dict:
            post['lu_%s' % code] = sync_from_dict[code]

        print()
        print('Attempting sync with the following parameters:')
        pprint(sync_from_dict)
        print()

        # do request
        url = '%s/api/pos/v2/sync' % settings.SALEBOX['API']['URL']
        try:
            r = requests.post(url, data=post)
            have_response = True
        except:
            print('Something went wrong: ConnectionError')
            have_response = False

        try:
            if have_response:
                response = r.json()
                # pprint(response)

                # display debug meta
                print('Output received (\'data\' attribute truncated to len(data)):')
                response_meta = r.json()

                # exit if connection error
                if response_meta['status'] != 'OK':
                    print('Connection error: %s' % response_meta['status'])
                    return

                # display meta object
                for code in response_meta['sync']:
                    code['data'] = len(code['data'])
                pprint(response_meta)
                print()
                print('Updating:')

                # save data
                for i, value in enumerate(response['sync']):
                    if value['code'] == 'attribute':
                        self.pull_model_attribute(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'attribute_item':
                        self.pull_model_attribute_item(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'country':
                        self.pull_model_country(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'country_state':
                        self.pull_model_country_state(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'country_state_translation':
                        self.pull_model_country_state_translation(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'country_translation':
                        self.pull_model_country_translation(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'discount_seasonal_group':
                        self.pull_model_discount_seasonal_group(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'discount_seasonal_ruleset':
                        self.pull_model_discount_seasonal_ruleset(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'member':
                        self.pull_model_member(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'member_group':
                        self.pull_model_member_group(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product':
                        self.pull_model_product(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product_category':
                        self.pull_model_product_category(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product_variant':
                        self.pull_model_product_variant(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    elif value['code'] == 'product_variant_image':
                        self.pull_model_product_variant_image(
                            value['data'],
                            value['lu'],
                            sync_from_dict
                        )

                    else:
                        print('Error: %s' % value['code'])

                return response['resync_now']
                # return False
        except:
            print('Something went wrong')
            return False

    def pull_get_sync_from_dict(self):
        lus = LastUpdate.objects.all()

        # populate dict
        lu = {}
        for l in lus:
            lu[l.code] = l.value

        # fill in the gaps
        for code in [
            'attribute',
            'attribute_item',
            'country',
            'country_state',
            'country_state_translation',
            'country_translation',
            # 'discount_seasonal_group',
            # 'discount_seasonal_ruleset',
            'member',
            'member_group',
            'product',
            'product_category',
            'product_variant',
            'product_variant_image',
        ]:
            if code not in lu:
                LastUpdate(code=code, value=0.0).save()
                lu[code] = 0.0

        return lu

    def pull_image(self, id, urlpath, dir):
        self.timer_set('saleboxsync_sync_start', time.time())
        self.timer_set('saleboxsync_pull_start', time.time())

        # ensure target dir exists
        target_dir = '%s/salebox/%s' % (settings.MEDIA_ROOT, dir)
        try:
            os.makedirs(target_dir)
        except:
            pass

        # fetch image
        try:
            url = '%s/%s' % (settings.SALEBOX['API']['URL'], urlpath)
            suffix = urlpath.split('.')[-1]
            filename = '%s.%s.%s' % (id, urlpath.split('/')[-1][0:6], suffix)
            target = '%s/%s' % (target_dir, filename)
            r = requests.get(url)
            if r.status_code == 200:
                open(target, 'wb').write(r.content)
                return filename, True
        except:
            pass

        return None, False

    def pull_images(self):
        # product category
        imgs = ProductCategory \
                .objects \
                .exclude(image__isnull=True) \
                .filter(local_image__isnull=True) \
                .filter(active_flag=True)
        for img in imgs:
            path, success = self.pull_image(img.id, img.image[1:], 'pospc')
            if success:
                img.local_image = path
                img.save()

        # product
        imgs = Product \
                .objects \
                .exclude(image__isnull=True) \
                .filter(local_image__isnull=True) \
                .filter(active_flag=True)
        for img in imgs:
            path, success = self.pull_image(img.id, img.image[1:], 'posp')
            if success:
                img.local_image = path
                img.save()

        # product variant
        imgs = ProductVariant \
                .objects \
                .exclude(image__isnull=True) \
                .filter(local_image__isnull=True) \
                .filter(active_flag=True)
        for img in imgs:
            path, success = self.pull_image(img.id, img.image[1:], 'pospv')
            if success:
                img.local_image = path
                img.save()

        # product variant image
        imgs = ProductVariantImage \
                .objects \
                .exclude(img__isnull=True) \
                .filter(local_img__isnull=True) \
                .filter(active_flag=True)
        for img in imgs:
            path, success = self.pull_image(img.id, img.img, 'pvi')
            if success:
                img.local_img = path
                img.save()

    def pull_model_attribute(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = Attribute.objects.get_or_create(id=d['id'])
                o.code = d['code']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'attribute',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Attribute' % len(data))
        except:
            pass

    def pull_model_attribute_item(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = AttributeItem.objects.get_or_create(id=d['id'])
                o.attribute = Attribute.objects.get(id=d['attribute'])
                o.slug = d['slug']
                o.value = d['value']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'attribute_item',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x AttributeItem' % len(data))
        except:
            pass

    def pull_model_country(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = Country.objects.get_or_create(id=d['id'])
                o.code_2 = d['code_2']
                o.code_3 = d['code_3']
                o.default = d['default']
                o.name = d['name']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'country',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Country' % len(data))
        except:
            pass

    def pull_model_country_state(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryState.objects.get_or_create(id=d['id'])
                o.country = Country.objects.get(id=d['country'])
                o.code_2 = d['code_2']
                o.name = d['name']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'country_state',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryState' % len(data))
        except:
            pass

    def pull_model_country_state_translation(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryStateTranslation.objects.get_or_create(id=d['id'])
                o.language = d['language']
                o.state = CountryState.objects.get(id=d['state'])
                o.value = d['value']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'country_state_translation',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryStateTranslation' % len(data))
        except:
            pass

    def pull_model_country_translation(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryTranslation.objects.get_or_create(id=d['id'])
                o.language = d['language']
                o.country = Country.objects.get(id=d['country'])
                o.value = d['value']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'country_translation',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryTranslation' % len(data))
        except:
            pass

    def pull_model_discount_seasonal_group(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        """
        self.pull_set_sync_from_dict(
            'discount_seasonal_group',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )
        """

    def pull_model_discount_seasonal_ruleset(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        """
        self.pull_set_sync_from_dict(
            'discount_seasonal_ruleset',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )
        """

    def pull_model_member(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                # retrieve lookups
                group = MemberGroup.objects.get(id=d['group'])
                parent = Member.objects.get_or_create(id=d['id'])
                try:
                    gwc = MemberGroup.objects.get(id=d['group_when_created'])
                except:
                    gwc = None

                # get parent
                parent = None
                if d['parent'] is not None:
                    parent, created = Member.objects.get_or_create(id=d['parent'])

                # country / states
                country = None
                country_state = None
                if d['country'] is not None:
                    country = Country.objects.get(id=d['country'])
                if d['country_state'] is not None:
                    country_state = CountryState.objects.get(id=d['country_state'])

                # create object
                o, created = Member.objects.get_or_create(id=d['id'])
                o.group = group
                o.parent = parent
                o.group_when_created = gwc
                o.country = country
                o.country_state = country_state

                # update
                for a in [
                    'active_flag',
                    'address_1',
                    'address_2',
                    'address_3',
                    'address_4',
                    'address_5',
                    'date_of_birth',
                    'email',
                    'gender',
                    'guid',
                    'id_card',
                    'join_date',
                    'name_first',
                    'name_last',
                    'phone_1',
                    'phone_2',
                    'postcode',
                    'salebox_member_id',
                    'status',
                    'string_1',
                    'string_2',
                    'string_3',
                    'string_4',
                    'string_5',
                    'string_6',
                    'string_7',
                    'string_8',
                    'string_9',
                    'string_10',
                    'string_11',
                    'string_12',
                    'string_13',
                    'string_14',
                    'title',
                ]:
                    setattr(o, a, d[a])

                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'member',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Member' % len(data))
        except:
            pass

    def pull_model_member_group(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = MemberGroup.objects.get_or_create(id=d['id'])
                o.name = d['name']
                o.flat_discount_percentage = d['flat_discount_percentage']
                o.can_be_parent = d['can_be_parent']
                o.default_group = d['default_group']
                o.active_flag = d['active_flag']
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'member_group',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x MemberGroup' % len(data))
        except:
            pass

    def pull_model_product(self, data, api_lu, sync_from_dict):
        def sync_attributes(product, attribute_number, id_list):
            attributes_changed = False
            attribute_m2m = getattr(product, 'attribute_%s' % attribute_number)

            # remove
            for a in attribute_m2m.all():
                if a.id not in id_list:
                    attribute_m2m.remove(a)
                    attributes_changed = True

            # add
            for id in id_list:
                ai = AttributeItem.objects.get(id=id)
                attribute_m2m.add(ai)
                attributes_changed = True

            # save
            if attributes_changed:
                product.save()

        try:
            for d in data:
                # create object
                o, created = Product.objects.get_or_create(id=d['id'])
                o.category = ProductCategory.objects.get(id=d['category'])

                # update
                for a in [
                    'active_flag',
                    'bestseller_rank',
                    'image',
                    'inventory_flag',
                    'name',
                    'season',
                    'sold_by',
                    'slug',
                    'string_1',
                    'string_2',
                    'string_3',
                    'string_4',
                    'vat_applicable',
                ]:
                    setattr(o, a, d[a])

                o.save()

                # sync attributes
                for i in range(1, 11):
                    sync_attributes(o, i, d['attribute_%s' % i])

            # update sync_from
            self.pull_set_sync_from_dict(
                'product',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Product' % len(data))
        except:
            pass

    def pull_model_product_category(self, data, api_lu, sync_from_dict):
        try:
            # pass #1: save with parent = None to avoid mptt errors
            for d in data:
                o, created = ProductCategory.objects.get_or_create(id=d['id'])
                o.parent = None
                o.active_flag = d['active_flag']
                o.image = d['image']
                o.name = d['name']
                o.seasonal_flag = d['seasonal_flag']
                o.slug = d['slug']
                o.short_name = d['short_name']
                setattr(o, o._mptt_meta.left_attr, d['mptt_left'])
                setattr(o, o._mptt_meta.level_attr, d['mptt_level'])
                setattr(o, o._mptt_meta.parent_attr, None)
                setattr(o, o._mptt_meta.right_attr, d['mptt_right'])
                setattr(o, o._mptt_meta.tree_id_attr, d['mptt_tree_id'])
                o.save()

            # pass #2: re-save the categories with parents (where applicable)
            for d in data:
                parent = None
                if d['parent'] is not None:
                    parent = ProductCategory.objects.get(id=d['parent'])

                o = ProductCategory.objects.get(id=d['id'])
                o.parent = parent
                setattr(o, o._mptt_meta.parent_attr, parent)
                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'product_category',
                True,
                sync_from_dict,
                api_lu
            )

            print('%s x ProductCategory' % len(data))
        except:
            pass

    def pull_model_product_variant(self, data, api_lu, sync_from_dict):
        def sync_attributes(variant, attribute_number, id_list):
            attributes_changed = False
            attribute_m2m = getattr(variant, 'attribute_%s' % attribute_number)

            # remove
            for a in attribute_m2m.all():
                if a.id not in id_list:
                    attribute_m2m.remove(a)
                    attributes_changed = True

            # add
            for id in id_list:
                ai = AttributeItem.objects.get(id=id)
                attribute_m2m.add(ai)
                attributes_changed = True

            # save
            if attributes_changed:
                variant.save()

        try:
            for d in data:
                # create object
                o, created = ProductVariant.objects.get_or_create(id=d['id'])
                o.product = Product.objects.get(id=d['product'])

                # update
                for a in [
                    'active_flag',
                    'available_to_order',
                    'available_on_pos',
                    'available_on_ecom',
                    'bestseller_rank',
                    'barcode',
                    'bo_name',
                    'color',
                    'date_1',
                    'date_2',
                    'ecommerce_description',
                    'image',
                    'int_1',
                    'int_2',
                    'int_3',
                    'int_4',
                    'loyalty',
                    'member_discount_applicable',
                    'name',
                    'plu',
                    'price',
                    'sale_percent',
                    'sale_price',
                    'shelf_expiry_type',
                    'shelf_life_days',
                    'shipping_weight',
                    'size',
                    'size_order',
                    'size_uom',
                    'sku',
                    'slug',
                    'string_1',
                    'string_2',
                    'string_3',
                    'string_4',
                    'warehouse_location',
                ]:
                    setattr(o, a, d[a])

                o.save()

                # sync attributes
                for i in range(1, 11):
                    sync_attributes(o, i, d['attribute_%s' % i])

            # update sync_from
            self.pull_set_sync_from_dict(
                'product_variant',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            # update the natural sort value
            if len(data) > 0:
                update_natural_sort(ProductVariant, 'name', 'name_sorted')

            print('%s x ProductVariant' % len(data))
        except:
            pass

    def pull_model_product_variant_image(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                # create object
                o, created = ProductVariantImage.objects.get_or_create(
                    id=d['id'],
                    variant=ProductVariant.objects.get(id=d['variant'])
                )

                # update
                for a in [
                    'active_flag',
                    'description',
                    'img',
                    'img_height',
                    'img_width',
                    'order',
                    'title'
                ]:
                    setattr(o, a, d[a])

                o.save()

            # update sync_from
            self.pull_set_sync_from_dict(
                'product_variant_image',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x ProductVariantImage' % len(data))
        except:
            pass

    def pull_set_sync_from_dict(self, code, increment, sync_from_dict, api_lu):
        if increment:
            if timezone.now().timestamp() - api_lu > 20:
                if api_lu == 0:
                    api_lu = 1.0
                else:
                    api_lu += 0.00001

        if api_lu > sync_from_dict[code]:
            lu = LastUpdate.objects.get(code=code)
            lu.value = float(api_lu)
            lu.save()
            cache.clear()  # TODO, this probably wants to be a setting, and
                           # better still, have a list of cache keys to
                           # void, rather than all

    def push_member(self, user):
        self.timer_set('saleboxsync_sync_start', time.time())

        # build post
        post = self.init_post()
        post['salebox_member_id'] = user.salebox_member_id
        post['salebox_member_sync'] = json.dumps(user.salebox_member_sync)

        # do request
        url = '%s/api/pos/v2/member-update' % settings.SALEBOX['API']['URL']
        try:
            r = requests.post(url, data=post)
            if r.status_code == 200:
                user.salebox_member_sync = None
                user.save()
                self.timer_set('saleboxsync_pull_start', 0.0)
        except:
            print('Failed to POST member data')

    def push_members(self):
        cutoff = timezone.now() - datetime.timedelta(seconds=10)
        users = get_user_model() \
                    .objects \
                    .filter(salebox_member_sync__isnull=False) \
                    .filter(salebox_last_update__lt=cutoff)
        for user in users:
            self.push_member(user)

    def push_transaction(self, store):
        # build POST
        data = self.init_post()
        data['transaction'] = json.dumps({
            'basket': self.transaction_basket(store),
            'invoice': self.transaction_invoice(store),
            'manual_discount': None,
            'member': self.transaction_member(store),
            'meta': self.transaction_meta(store),
            'payment': self.transaction_payment(store),
            'shipping': self.transaction_shipping(store),
            'stored_value_load': None,
            'total': self.transaction_total(store)
        })

        # send
        url = '%s/api/pos/v2/transaction' % settings.SALEBOX['API']['URL']
        try:
            r = requests.post(url, data=data)
            have_response = True
        except:
            print('Something went wrong: ConnectionError')
            have_response = False

        # check response
        if have_response:
            if r.json()['status'] == 'OK':
                store.status = 31
                store.save()

    def push_transactions(self):
        css = CheckoutStore.objects.filter(status=30)
        for cs in css:
            self.timer_set('saleboxsync_sync_start', time.time())

            # ensure this user has a corresponding salebox_member
            if cs.user is not None:
                user = get_user_model().objects.get(id=cs.user)
                member = Member.objects.filter(salebox_member_id=user.salebox_member_id).first()
                if member is None:
                    # skip for now, get on the next time round
                    if user.salebox_member_sync is None:
                        user.set_salebox_member_sync('email', user.email)
                    continue

            # push transaction
            self.push_transaction(cs)

    def timer_get(self, code, default_value=0.0):
        try:
            return LastUpdate.objects.get(code=code).value
        except:
            LastUpdate(code=code, value=default_value).save()
            return default_value

    def timer_set(self, code, value):
        o = LastUpdate.objects.get(code=code)
        o.value = value
        o.save()

    def transaction_basket(self, store):
        basket = []
        for b in store.data['basket']['items']:
            v = b['variant']

            basket.append({
                'discount_ruleset': None,
                'loyalty': v['loyalty'],
                'price_original': v['qty_price'],
                'price_modified': v['qty_sale_price'],
                'product_weight': None,
                'quantity': b['qty'],
                'shipping_weight': v['shipping_weight'],
                'unit_price': v['price'],
                'variant_id': v['id'],
            })

        return basket

    def transaction_invoice(self, store):
        data = store.data['invoice_address']

        # invoice not requested
        if not data['required']:
            return None

        # invoice requested, populate data
        return {
            'address_1': data['address']['address_1'],
            'address_2': data['address']['address_2'],
            'address_3': data['address']['address_3'],
            'address_4': data['address']['address_4'],
            'address_5': data['address']['address_5'],
            'country_state_id': data['address']['country_state'],
            'country_id': data['address']['country'],
            'postcode': data['address']['postcode'],
            'recipient_name': data['address']['full_name'],
            'recipient_tax_id': data['address']['tax_id']
        }

    def transaction_member(self, store):
        if store.user is None:
            return None

        # retrieve user
        user = get_user_model().objects.get(id=store.user)
        return {
            "salebox_member_id": str(user.salebox_member_id),
            "total_loyalty": store.data['basket']['loyalty']
        }

    def transaction_meta(self, store):
        return {
            'guid': store.visible_id,
            'user_id': settings.SALEBOX['MISC']['POS_USER_ID'],
            'utc': [
                store.last_updated.year,
                store.last_updated.month,
                store.last_updated.day,
                store.last_updated.hour,
                store.last_updated.minute,
                store.last_updated.second,
                store.last_updated.microsecond,
            ]
        }

    def transaction_payment(self, store):
        total_price = (
            store.data['basket']['sale_price'] +
            store.data['shipping_method']['price']
        )

        return [
            {
                "amount_change": 0,
                "amount_tendered": total_price,
                "method_id": store.data['payment_method']['id']
            }
        ]

    def transaction_shipping(self, store):
        address = store.data['shipping_address']
        method = store.data['shipping_method']

        # shipping not requested
        if not address['required']:
            return None

        # shipping requested, populate data
        return {
            'address_1': address['address']['address_1'],
            'address_2': address['address']['address_2'],
            'address_3': address['address']['address_3'],
            'address_4': address['address']['address_4'],
            'address_5': address['address']['address_5'],
            'country_id': address['address']['country'],
            'country_state_id': address['address']['country_state'],
            'method_id': method['id'],
            'postcode': address['address']['postcode'],
            'price': method['price'],
            'recipient_name': address['address']['full_name']
        }

    def transaction_total(self, store):
        vat_rate = settings.SALEBOX['MISC']['VAT_RATE']

        # calculate gross + gross_vat_applicable
        gross_total = 0
        gross_vat_applicable = 0
        for b in store.data['basket']['items']:
            gross_total += b['variant']['qty_sale_price']
            if b['variant']['product']['vat_applicable']:
                gross_vat_applicable += b['variant']['qty_sale_price']

        # calculate
        total_vat = round(gross_vat_applicable / (1 + (vat_rate / 100)))
        return {
            'total_gross': gross_total,
            'total_net': gross_total - total_vat,
            'total_vat': total_vat,
            'vat_rate': vat_rate
        }
