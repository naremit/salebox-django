from django.http import JsonResponse

from saleboxdjango.forms import RatingForm
from saleboxdjango.models import ProductVariant, ProductVariantRating


def rating_ajax_view(request):
    if request.user.is_authenticated and request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            variant = ProductVariant \
                        .objects \
                        .get(id=form.cleaned_data['variant_id'])

            # delete
            if form.cleaned_data['rating'] == -1:
                o = ProductVariantRating \
                        .objects \
                        .filter(user=request.user) \
                        .filter(variant=variant) \
                        .first()

                if o is not None:
                    o.delete()

            # add
            else:
                o, created = ProductVariantRating \
                                .objects \
                                .get_or_create(user=request.user, variant=variant)
                o.rating = form.cleaned_data['rating']
                o.save()

    return JsonResponse({})