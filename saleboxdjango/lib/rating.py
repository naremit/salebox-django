from django.db.models import Avg, Sum
from django.http import JsonResponse

from saleboxdjango.models import ProductVariant, ProductVariantRating
from saleboxdjango.lib.common import get_rating_display


class SaleboxRating:
    def __init__(self, user=None):
        self.user = user

    def add_rating(self, rating):
        if self.user is not None:
            pvs = ProductVariantRating \
                        .objects \
                        .filter(variant=self.variant) \
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
            o['global_product_rating'] = self.get_global_product_rating()

        if 'global_variant_rating' in results:
            o['global_variant_rating'] = self.get_global_variant_rating()

        if 'user_variant_rating' in results:
            o['user_rating'] = self.get_user_variant_rating()

        return o

    def get_global_product_rating(self):
        count = self.variant.product.rating_vote_count
        rating = self.variant.product.rating_score
        return {
            'count': count,
            'rating': rating_display(rating, count)
        }

    def get_global_variant_rating(self):
        count = self.variant.rating_vote_count
        rating = self.variant.rating_score
        return {
            'count': count,
            'rating': rating_display(rating, count)
        }

    def get_user_variant_rating(self):
        if self.user is not None:
            try:
                return ProductVariantRating \
                        .objects \
                        .filter(variant=self.variant) \
                        .filter(user=self.user)[0].rating
            except:
                pass

        return None

    def remove_rating(self):
        if self.user is not None:
            pvs = ProductVariantRating \
                    .objects \
                    .filter(variant=self.variant) \
                    .filter(user=self.user)

            for pv in pvs:
                pv.delete()

    def set_variant(self, variant_id):
        self.variant_id = variant_id
        self.variant = ProductVariant \
                        .objects \
                        .select_related('product') \
                        .get(id=self.variant_id)
