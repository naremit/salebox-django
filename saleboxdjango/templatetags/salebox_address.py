from django import template
from django.utils.translation import get_language

from saleboxdjango.lib.translation import get_translation
from saleboxdjango.models import Country, CountryState

register = template.Library()

@register.simple_tag
def sb_country_name(country, default='', lang=None):
    if isinstance(country, dict):
        country = country['id']
    if isinstance(country, int):
        country = Country.objects.get(id=country)
    if not isinstance(country, Country):
        return default

    if lang is None:
        lang = (get_language()).lower().split('-')[0]

    return get_translation(
        lang,
        'place.%s' % country.code,
        default
    )


@register.simple_tag
def sb_country_state_name(country_state, default='', lang=None):
    if isinstance(country_state, dict):
        country_state = country_state['id']
    if isinstance(country_state, int):
        country_state = CountryState.objects.get(id=country_state)
    if not isinstance(country_state, CountryState):
        return default

    if lang is None:
        lang = (get_language()).lower().split('-')[0]

    return get_translation(
        lang,
        'place.%s' % country_state.full_code,
        default
    )
