from django.http import Http404
from django.shortcuts import get_object_or_404

from saleboxdjango.lib.common import image_path, price_display, get_rating_dict
from saleboxdjango.models import ProductVariant, ProductVariantRating


def get_product_detail(request, variant_id, variant_slug):
    variant_slug = variant_slug.strip('/')

    try:
        variant_id = int(variant_id)
        variant_slug = str(variant_slug)
    except:
        raise Http404()

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

    # get ratings
    rating = {
        'logged_in_user': get_rating_dict(0, 0),
        'global': get_rating_dict(variant.rating_score, variant.rating_vote_count)
    }

    # get logged in user's rating
    if request.user.is_authenticated:
        pvr = ProductVariantRating \
                .objects \
                .filter(user=request.user) \
                .filter(variant=variant) \
                .first()
        if pvr:
            rating['logged_in_user'] = get_rating_dict(pvr.rating, 1)

    # build context
    return {
        'in_basket': str(variant.id) in request.session['basket']['basket']['contents'],
        'in_wishlist': variant.id in request.session['basket']['wishlist']['contents'],
        'price': price_display(variant.price),
        'product': product,
        'rating': rating,
        'siblings': siblings,
        'variant': variant
    }
