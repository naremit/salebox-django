import json

from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.utils.translation import get_language

from saleboxdjango.lib.translation import get_translation, get_translations
from saleboxdjango.models import Country, CountryState, UserAddress


class SaleboxAddress:
    def __init__(self, user, address_group='default'):
        self.user = user
        if self.user.is_authenticated:
            self.query = UserAddress \
                            .objects \
                            .filter(user=user) \
                            .filter(address_group=address_group) \
                            .filter(active_flag=True) \
                            .select_related('country', 'country_state')

    def add(self, values):
        # get country
        if isinstance(values['country'], int):
            values['country'] = \
                Country.objects.get(id=values['country'])

        # get country_state
        if isinstance(values['country_state'], int):
            values['country_state'] = \
                CountryState.objects.get(id=values['country_state'])

        # create address instance
        address = UserAddress(
            default=values['default'] or False,
            address_group=values['address_group'] or 'default',
            full_name=values['full_name'],
            address_1=values['address_1'],
            address_2=values['address_2'],
            address_3=values['address_3'],
            address_4=values['address_4'],
            address_5=values['address_5'],
            country_state=values['country_state'],
            country=values['country'],
            postcode=str(values['postcode'] or '').upper(),
            phone_1=values['phone_1'],
            phone_2=values['phone_2'],
            email=values['email'],
            string_1=values['string_1'],
            string_2=values['string_2'],
            tax_id=values['tax_id']
        )

        # save to db if user is authenticated
        if self.user.is_authenticated:
            address.user=self.user
            address.save()

        return address

    def form_extras(self, country_id=None):
        country_list = self._get_country_list()
        country_state_lookup = self._get_country_state_lookup()

        # build 'current' country_state list
        try:
            current_country_states = country_state_lookup[int(country_id)]
        except:
            current_country_states = []

        # build javascript country_state dict
        js_country_states = \
            json.dumps(country_state_lookup, ensure_ascii=False) \
                .replace('"id": ', 'i:') \
                .replace(', "name": ', ',s:') \
                .replace('}, {', '},{')

        return {
            'country_list': country_list,
            'current_states': current_country_states,
            'js_states': js_country_states
        }

    def get(
            self,
            selected_id=None,
            force_selected=False,
            non_null_fields=[]
        ):
            # return an empty list for non-authenticated users
            if not self.user.is_authenticated:
                return []

            # get addresses
            addresses = self.query.all()
            if 'tax_id' in non_null_fields:
                addresses = addresses.filter(tax_id__isnull=False)

            # add 'selected' value and localised country name
            for a in addresses:
                a.selected = False
                # a.country_name = self._get_country_name(a.country)
                # a.country_state_name = self._get_country_state_name(a.country_state)

            # set selected_id if exists
            has_selected = False
            for a in addresses:
                if a.id == selected_id:
                    a.selected = True
                    has_selected = True

            # force selection of an address
            if force_selected and not has_selected and len(addresses) > 0 :
                # select the default address
                for a in addresses:
                    if a.default:
                        a.selected = True
                        has_selected = True
                        break

                # fall back to the first address
                if not has_selected:
                    addresses[0].selected = True

            # return
            return addresses

    def get_count(self):
        return self.query.all().count()

    def set_default(self, address_id):
        address = self._get_address_by_id(address_id)
        if address is not None and not address.default:
            address.default = True
            address.save()

    def set_inactive(self, address_id):
        address = self._get_address_by_id(address_id)
        if address is not None:
            address.active_flag = False
            address.save()

    def _get_address_by_id(self, address_id):
        return self.query.all().filter(id=address_id).first()

    def _get_allowed_countries(self):
        try:
            return settings.SALEBOX['MISC']['ALLOWED_COUNTRIES']
        except:
            return []

    def _get_country_list(self):
        lang = get_language()

        countries = Country.objects.all()
        allowed_countries = self._get_allowed_countries()
        if len(allowed_countries) > 0:
            countries = countries.filter(id__in=allowed_countries)
        countries = list(countries.values('id', 'code'))

        # get translated name
        for c in countries:
            c['name'] = get_translation(
                lang,
                'place.%s' % c['code'],
                c['code']
            )
            del c['code']

        # sort
        countries = sorted(countries, key=lambda k: k['name'])
        return countries

    def _get_country_state_lookup(self):
        lang = get_language()
        i18n = get_translations()

        states_list = CountryState.objects.all()
        allowed_countries = self._get_allowed_countries()
        if len(allowed_countries) > 0:
            states_list = states_list.filter(country__id__in=allowed_countries)
        states_list = list(states_list.values('id', 'country__id', 'full_code'))

        # create a lookup
        lookup = {}
        for s in states_list:
            lookup[s['id']] = {
                'country': s['country__id'],
                'name': get_translation(
                    lang,
                    'place.%s' % s['full_code'],
                    translations=i18n
                )
            }

        # create dict of states per country
        countries = {}
        for key in lookup:
            if lookup[key]['country'] not in countries:
                countries[lookup[key]['country']] = []
            countries[lookup[key]['country']].append({
                'id': key,
                'name': lookup[key]['name']
            })

        # sort each country
        if not lang.startswith('en'):
            for c in countries:
                countries[c] = sorted(countries[c], key=lambda k: k['name'])

        return countries
