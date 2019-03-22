import datetime
import os
import requests
import time
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from saleboxdjango.models import *


class Command(BaseCommand):
    def handle(self, *args, **options):
        do_sync = cache.get('saleboxsync') is None

        # sync data
        while do_sync:
            try:
                cache.set('saleboxsync', 1, 60)
                do_sync = self.do_sync()
                time.sleep(2)
            except:
                do_sync = False

        # sync images
        self.get_images()
        cache.delete('saleboxsync')

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
                for code in response_meta['sync']:
                    code['data'] = len(code['data'])
                pprint(response_meta)
                print()
                print('Updating:')

                # save data
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

                        elif value['code'] == 'country':
                            self.sync_country(
                                value['data'],
                                value['lu'],
                                sync_from_dict
                            )

                        elif value['code'] == 'country_state':
                            self.sync_country_state(
                                value['data'],
                                value['lu'],
                                sync_from_dict
                            )

                        elif value['code'] == 'country_state_translation':
                            self.sync_country_state_translation(
                                value['data'],
                                value['lu'],
                                sync_from_dict
                            )

                        elif value['code'] == 'country_translation':
                            self.sync_country_translation(
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

                        elif value['code'] == 'product_variant_image':
                            self.sync_product_variant_image(
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

    def get_image(self, id, urlpath, dir):
        cache.set('saleboxsync', 1, 60)

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

    def get_images(self):
        # product category
        imgs = ProductCategory \
                .objects \
                .exclude(image__isnull=True) \
                .filter(local_image__isnull=True) \
                .filter(active_flag=True)
        for img in imgs:
            path, success = self.get_image(img.id, img.image[1:], 'pospc')
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
            path, success = self.get_image(img.id, img.image[1:], 'posp')
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
            path, success = self.get_image(img.id, img.image[1:], 'pospv')
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
            path, success = self.get_image(img.id, img.img, 'pvi')
            if success:
                img.local_img = path
                img.save()

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

    def set_sync_from_dict(self, code, increment, sync_from_dict, api_lu):
        if increment:
            if now().timestamp() - api_lu > 60:
                if api_lu == 0:
                    api_lu = 1.0
                else:
                    api_lu += 0.00001

        if api_lu > sync_from_dict[code]:
            lu = LastUpdate.objects.get(code=code)
            lu.value = float(api_lu)
            lu.save()
            cache.clear()  # TODO, this probable wants to be a setting, and better still, have a list of cache keys to void, rather than all

    def sync_attribute(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = Attribute.objects.get_or_create(id=d['id'])
                o.code = d['code']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'attribute',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Attribute' % len(data))
        except:
            pass

    def sync_attribute_item(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = AttributeItem.objects.get_or_create(id=d['id'])
                o.attribute = Attribute.objects.get(id=d['attribute'])
                o.slug = d['slug']
                o.value = d['value']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'attribute_item',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x AttributeItem' % len(data))
        except:
            pass

    def sync_country(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = Country.objects.get_or_create(id=d['id'])
                o.code_2 = d['code_2']
                o.code_3 = d['code_3']
                o.default = d['default']
                o.name = d['name']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'country',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Country' % len(data))
        except:
            pass

    def sync_country_state(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryState.objects.get_or_create(id=d['id'])
                o.country = Country.objects.get(id=d['country'])
                o.code_2 = d['code_2']
                o.name = d['name']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'country_state',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryState' % len(data))
        except:
            pass

    def sync_country_state_translation(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryStateTranslation.objects.get_or_create(id=d['id'])
                o.language = d['language']
                o.state = CountryState.objects.get(id=d['state'])
                o.value = d['value']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'country_state_translation',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryStateTranslation' % len(data))
        except:
            pass

    def sync_country_translation(self, data, api_lu, sync_from_dict):
        try:
            for d in data:
                o, created = CountryTranslation.objects.get_or_create(id=d['id'])
                o.language = d['language']
                o.country = Country.objects.get(id=d['country'])
                o.value = d['value']
                o.save()

            # update sync_from
            self.set_sync_from_dict(
                'country_translation',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x CountryTranslation' % len(data))
        except:
            pass

    def sync_discount_seasonal_group(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        """
        self.set_sync_from_dict(
            'discount_seasonal_group',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )
        """

    def sync_discount_seasonal_ruleset(self, data, api_lu, sync_from_dict):
        # for d in data
        #
        #

        # update sync_from
        """
        self.set_sync_from_dict(
            'discount_seasonal_ruleset',
            len(data) < 100,
            sync_from_dict,
            api_lu
        )
        """

    def sync_member(self, data, api_lu, sync_from_dict):
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
            self.set_sync_from_dict(
                'member',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Member' % len(data))
        except:
            pass

    def sync_member_group(self, data, api_lu, sync_from_dict):
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
            self.set_sync_from_dict(
                'member_group',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x MemberGroup' % len(data))
        except:
            pass

    def sync_product(self, data, api_lu, sync_from_dict):
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
            self.set_sync_from_dict(
                'product',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x Product' % len(data))
        except:
            pass

    def sync_product_category(self, data, api_lu, sync_from_dict):
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
            self.set_sync_from_dict(
                'product_category',
                True,
                sync_from_dict,
                api_lu
            )

            print('%s x ProductCategory' % len(data))
        except:
            pass

    def sync_product_variant(self, data, api_lu, sync_from_dict):
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
                    'loyalty_points',
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
            self.set_sync_from_dict(
                'product_variant',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x ProductVariant' % len(data))
        except:
            pass

    def sync_product_variant_image(self, data, api_lu, sync_from_dict):
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
            self.set_sync_from_dict(
                'product_variant_image',
                len(data) < 100,
                sync_from_dict,
                api_lu
            )

            print('%s x ProductVariantImage' % len(data))
        except:
            pass

