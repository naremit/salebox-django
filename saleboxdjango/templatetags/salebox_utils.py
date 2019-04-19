from math import modf

from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(is_safe=True)
def sb_currency(value):
    minor, major = modf(value / 100)
    return mark_safe('%s<span>.%s</span>' % \
        (intcomma(int(major)), '{:.2f}'.format(minor)[2:]))