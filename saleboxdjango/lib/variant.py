from django.db.models import Case, BooleanField, Value, When

from saleboxdjango.lib.common import get_price_display
from saleboxdjango.models import ProductVariant


def get_sibling_variants(variant, order_by=None):
    pvs = ProductVariant \
            .objects \
            .filter(active_flag=True) \
            .filter(available_on_ecom=True) \
            .filter(product__active_flag=True) \
            .filter(product__category__active_flag=True) \
            .filter(product=variant.product) \
            .annotate(selected_variant=Case(
                When(id=variant.id, then=True),
                default=Value(False),
                output_field=BooleanField(),
            ))

    if order_by is not None:
        pvs = pvs.order_by(order_by)

    for pv in pvs:
        pv.price_display = get_price_display(pv.price)

    return pvs
