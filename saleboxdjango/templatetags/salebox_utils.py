from django import template
from django.utils.safestring import mark_safe

from saleboxdjango.lib.common import get_price_display
register = template.Library()

@register.simple_tag
def sb_price_display_formatted_html(*args):
    return mark_safe(get_price_display(sum(args))['formatted_html'])


