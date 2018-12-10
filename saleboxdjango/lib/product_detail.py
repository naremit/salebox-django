from django.shortcuts import get_object_or_404

from saleboxdjango.lib.common import image_path, price_display
from saleboxdjango.models import ProductVariant, ProductVariantRating


def get_product_detail(request, variant_id, variant_slug):
    # get variant
    variant = get_object_or_404(
        ProductVariant,
        id=variant_id,
        slug=variant_slug,
        active_flag=True,
        available_on_ecom=True
    )

    # update image paths
    product = variant.product
    product.image = image_path(product.image)
    variant.image = image_path(variant.image)

    # get sibling variants
    siblings = ProductVariant \
                    .objects \
                    .filter(product=variant.product) \
                    .exclude(id=variant.id) \
                    .filter(active_flag=True) \
                    .filter(available_on_ecom=True)

    # get user's score
    score = None
    if request.user.is_authenticated:
        pvr = ProductVariantRating \
                .objects \
                .filter(user=request.user) \
                .filter(variant=variant)
        if len(pvr) > 0:
            score = pvr[0].score

    # build context
    return {
        'in_basket': str(variant.id) in request.session['basket']['basket'],
        'in_wishlist': variant.id in request.session['basket']['wishlist'],
        'price': price_display(variant.price),
        'product': product,
        'score': score,
        'score_10': round(score / 10) if score else None,
        'score_5': round(score / 20) if score else None,
        'siblings': siblings,
        'variant': variant
    }
