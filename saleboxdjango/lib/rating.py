from django.db.models import Avg, Sum
from django.http import JsonResponse

from saleboxdjango.models import Product, ProductVariant, \
    ProductVariantRating
from saleboxdjango.lib.common import get_rating_display


class SaleboxRating:
    def __init__(self, user=None):
        self.user = user
        self.variant = None  # set via the set_variant_from_id method below

    # used by SaleboxRatingAddView / SaleboxRatingRemoveView to provide rating
    # scores for the variant just modified
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

    # get the score for a single product (all votes)
    def get_global_product_rating(self):
        if self.variant is None:
            raise ValueError('SaleboxRating product variant not set')
        p = Product.objects.get(id=self.variant.product.id)
        return self._return_rating(p.rating_vote_count, p.rating_score)

    # get the score for a single variant (all votes)
    def get_global_variant_rating(self):
        if self.variant is None:
            raise ValueError('SaleboxRating product variant not set')
        pv = ProductVariant.objects.get(id=self.variant.id)
        return self._return_rating(pv.rating_vote_count, pv.rating_score)

    # get the score for a single variant (current user's vote only)
    def get_user_variant_rating(self):
        if self.user is not None:
            if self.variant is None:
                raise ValueError('SaleboxRating product variant not set')

            pvr = ProductVariantRating \
                        .objects \
                        .filter(variant=self.variant) \
                        .filter(user=self.user) \
                        .first()

            if pvr is None:
                return self._return_rating(0, 0)
            else:
                return self._return_rating(1, pvr.rating)

        return None

    # add (or update an existing) variant rating
    def rating_add(self, rating):
        if self.user is not None:
            if self.variant is None:
                raise ValueError('SaleboxRating product variant not set')

            pvr = ProductVariantRating \
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

    # remove a variant rating
    def rating_remove(self):
        if self.user is not None:
            if self.variant is None:
                raise ValueError('SaleboxRating product variant not set')

            pvs = ProductVariantRating \
                    .objects \
                    .filter(variant=self.variant) \
                    .filter(user=self.user)

            for pv in pvs:
                pv.delete()

    # fetch the applicable variant
    def set_variant_from_id(self, variant_id):
        self.variant_id = variant_id
        self.variant = ProductVariant \
                        .objects \
                        .select_related('product') \
                        .get(id=self.variant_id)

    # private function to return results as a dict
    def _return_rating(self, count, rating):
        return {
            'count': count,
            'rating': get_rating_display(rating, count)
        }