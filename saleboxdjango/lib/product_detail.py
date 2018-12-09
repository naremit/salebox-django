from django.shortcuts import get_object_or_404

from saleboxdjango.models import ProductVariant


def get_variant_or_404(variant_id, variant_slug):
    return get_object_or_404(
        ProductVariant,
        id=variant_id,
        slug=variant_slug,
        active_flag=True,
        available_on_ecom=True
    )

def get_sibling_variants(variant):
    return ProductVariant \
            .objects \
            .filter(product=variant.product) \
            .exclude(id=variant.id) \
            .filter(active_flag=True) \
            .filter(available_on_ecom=True) \
