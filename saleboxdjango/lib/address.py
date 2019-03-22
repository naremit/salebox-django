from django.http import JsonResponse
from django.template.loader import render_to_string

from saleboxdjango.forms import SaleboxAddressAddForm
from saleboxdjango.models import Country, CountryState, CountryTranslation, \
    CountryStateTranslation, UserAddress


class SaleboxAddress:
    def __init__(self, user, address_group='default'):
        self.query = UserAddress \
                        .objects \
                        .filter(user=user) \
                        .filter(address_group=address_group) \
                        .select_related('country', 'country_state')

    def add_form(
            self,
            request,
            state=None,
            lang=None,
            default_country_id=None,
            form_name='salebox_address_add',
            form_class=SaleboxAddressAddForm,
            template='salebox/address/add.html'
        ):
        status = 'unbound'
        form = form_class()
        address = None

        if request.user.is_authenticated:
            if request.method == 'POST' and request.POST.get('form_name') == form_name:
                form = form_class(request.POST)
                if form.is_valid():
                    country = None
                    country_state = None
                    if form.cleaned_data['country'] is not None:
                        country = Country \
                                    .objects \
                                    .get(id=form.cleaned_data['country'])
                    if form.cleaned_data['country_state'] is not None:
                        country_state = CountryState \
                                            .objects \
                                            .get(id=form.cleaned_data['country_state'])

                    status = 'success'
                    address = UserAddress(
                        user=request.user,
                        default=form.cleaned_data['default'],
                        address_group=form.cleaned_data['address_group'] or 'default',
                        full_name=form.cleaned_data['full_name'],
                        address_1=form.cleaned_data['address_1'],
                        address_2=form.cleaned_data['address_2'],
                        address_3=form.cleaned_data['address_3'],
                        address_4=form.cleaned_data['address_4'],
                        address_5=form.cleaned_data['address_5'],
                        country_state=country_state,
                        country=country,
                        postcode=form.cleaned_data['postcode'].upper()
                    )
                    address.save()
                else:
                    status = 'error'
            else:
                form.fields['country'].initial = default_country_id
        else:
            status = 'unauthenticated'

        return (
            status,
            address,
            render_to_string(
                template,
                context={
                    'countries': self._get_countries(lang),
                    'form': form,
                    'form_name': form_name,
                    'state': state,
                    'states': self._get_states(lang),
                },
                request=request
            ),
            state
        )

    def get_count(self):
        return self.query.all().count()

    def get_list(
            self,
            selected_id=None,
            csv_vars='address_1,address_2,address_3,address_4,address_5,country_state,country,postcode',
            lang=None
        ):
        addresses = self.query.all()

        # add "selected" attribute to all addresses
        if len(addresses) > 0:
            has_selected = False
            for a in addresses:
                a.selected = False
                if a.id == selected_id:
                    a.selected = True
                    has_selected = True

            if not has_selected:
                for a in addresses:
                    if a.default:
                        a.selected = True
                        break

        # make a list of the non-null address lines
        csv_vars = csv_vars.split(',')
        for a in addresses:
            a.address_list = []
            for csv in csv_vars:
                if csv == 'country':
                    tmp = self._get_country(a.country, lang)
                elif csv == 'country_state':
                    tmp = self._get_state(a.country_state, lang)
                else:
                    tmp = getattr(a, csv, None)

                if tmp is not None and len(tmp) > 0:
                    a.address_list.append(tmp)

        return addresses

    def get_single_by_default(self):
        return self.query.all().get(default=True)

    def get_single_by_id(self, id):
        return self.query.all().get(id=id)

    def remove_address(self, id):
        address = self.query.all().get(id=id)
        address.delete()

    def render_list(
            self,
            addresses,
            show_checkbox=False,
            template='salebox/address/list.html'
        ):

        return render_to_string(
            template,
            {
                'addresses': addresses,
                'show_checkbox': show_checkbox
            }
        )

    def set_default(self, id):
        address = self.get_single_by_id(id)
        if not address.default:
            address.default = True
            address.save()

    def _get_country(self, country, lang):
        if country is None:
            return None
        elif lang is not None:
            i18n = CountryTranslation \
                    .objects \
                    .filter(language=lang) \
                    .filter(country=country) \
                    .first()
            if i18n is not None:
                return i18n.value

        return country.name

    def _get_countries(self, lang):
        countries = list(Country.objects.all().values('id', 'name'))

        # translate if req'd
        if lang is not None:
            # get translations from database
            lookup = {}
            i18n = CountryTranslation.objects.all().values('country__id', 'value')
            for c in i18n:
                lookup[c['country__id']] = c['value']

            # replace labels
            for c in countries:
                if c['id'] in lookup:
                    c['name'] = lookup[c['id']]

            # sort
            countries = sorted(countries, key=lambda k: k['name'])

        return countries

    def _get_state(self, state, lang):
        if state is None:
            return None
        elif lang is not None:
            i18n = CountryStateTranslation \
                    .objects \
                    .filter(language=lang) \
                    .filter(state=state) \
                    .first()
            if i18n is not None:
                return i18n.value

        return state.name

    def _get_states(self, lang):
        states_list = list(
            CountryState
                .objects
                .all()
                .values('id', 'country__id', 'name')
        )

        # create a lookup
        lookup = {}
        for s in states_list:
            lookup[s['id']] = {
                'country': s['country__id'],
                'name': s['name']
            }

        # translate if req'd
        if lang is not None:
            i18n = CountryStateTranslation.objects.all().values('state__id', 'value')
            for i in i18n:
                lookup[i['state__id']]['name'] = i['value']

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
        if lang is not None:
            for c in countries:
                countries[c] = sorted(countries[c], key=lambda k: k['name'])

        return countries
