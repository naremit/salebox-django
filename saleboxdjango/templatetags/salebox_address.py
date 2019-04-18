from django import template
from django.utils.translation import get_language

from saleboxdjango.models import Country, CountryState, CountryTranslation, CountryStateTranslation

register = template.Library()

@register.simple_tag
def sb_country_name(country, default='', lang=None):
    if country is None:
        return default

    if isinstance(country, int):
        country = Country.objects.get(id=country)

    if lang is None:
        lang = (get_language()).lower().split('-')[0]

    if lang != 'en':
        i18n = CountryTranslation \
                .objects \
                .filter(language=lang) \
                .filter(country=country) \
                .first()
        if i18n is not None:
            return i18n.value

    # fallback to English
    return country.name

@register.simple_tag
def sb_country_state_name(country_state, default='', lang=None):
    if country_state is None:
        return default

    if isinstance(country_state, int):
        country_state = CountryState.objects.get(id=country_state)

    if lang is None:
        lang = (get_language()).lower().split('-')[0]

    if lang != 'en':
        i18n = CountryStateTranslation \
                .objects \
                .filter(language=lang) \
                .filter(state=country_state) \
                .first()
        if i18n is not None:
            return i18n.value

    # fallback to English
    return country_state.name
