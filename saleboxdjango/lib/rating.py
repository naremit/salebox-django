from django.db.models import Avg
from django.http import JsonResponse

from saleboxdjango.forms import RatingForm
from saleboxdjango.models import ProductVariant, ProductVariantRating
from saleboxdjango.lib.common import get_rating_display


class SaleboxRating:
    def __init__(self, variant_id, user=None):
        self.variant_id = variant_id
        self.user = user
        self.variant = ProductVariant \
                        .objects \
                        .get(id=variant_id) \
                        .select_related('product')

    def add_rating(self, user, rating):
        if self.user is not None:
            pvs = ProductVariantRating \
                        .objects \
                        .filter(variant=variant) \
                        .filter(user=self.user)

            if len(pvs) > 0:
                pvs[0].rating = rating
                pvs[0].save()
                for pv in pvs[1:]:
                    pv.delete()
            else:
                pv = ProductVariantRating(
                    user=self.user,
                    variant=self.variant,
                    rating=rating
                )
                pv.save()

    def get_data(self, results):
        results = results.split(',')
        o = {}

        if 'global_product_rating' in results:
            o['global_product_rating']  self.get_global_product_rating()

        if 'global_variant_rating' in results:
            o['global_variant_rating']  self.get_global_variant_rating()

        if 'user_variant_rating' in results:
            o['user_rating']  self.get_user_variant_rating()

        return o

    def get_global_product_rating(self):
        variant_ids = ProductVariant \
                        .objects \
                        .filter(product=variant.product) \
                        .values_list('id', flat=True)

        count = ProductVariantRating \
                    .objects \
                    .filter(variant__in=variant_ids) \
                    .count()

        if count > 0:
            return {
                'count': count,
                'rating': ProductVariantRating \
                            .objects \
                            .filter(variant__in=variant_ids) \
                            .aggregate(rating=Avg('rating_rating'))[0].rating
            }
        else:
            return {
                'count': 0,
                'rating': None
            }

    def get_global_variant_rating(self):
        count = ProductVariantRating \
                    .objects \
                    .filter(variant=variant) \
                    .count()

        if count > 0:
            return {
                'count': count,
                'rating': ProductVariantRating \
                            .objects \
                            .filter(variant=variant) \
                            .aggregate(rating=Avg('rating_rating'))[0].rating
            }
        else:
            return {
                'count': 0,
                'rating': None
            }

    def get_user_variant_rating(self):
        if self.user is not None:
            try:
                return ProductVariantRating \
                        .objects \
                        .filter(variant=variant) \
                        .filter(user=self.user)[0].rating_rating
            except:
                pass

        return None

    def remove_rating(self, user):
        if self.user is not None:
            pvs = ProductVariantRating \
                        .objects \
                        .filter(variant=variant) \
                        .filter(user=self.user)

            for pv in pvs:
                pv.delete()
