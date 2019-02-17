from django.core.cache import cache

from saleboxdjango.models import Product, ProductCategory, ProductVariant
from saleboxdjango.lib.common import image_path


class SaleboxCategory:
    def __init__(self):
        self.populated_categories_only = True
        self.product_attributes_include = []
        self.product_attributes_exclude = []
        self.variant_attributes_include = []
        self.variant_attributes_exclude = []

        self.valid_ids = []

    def get_tree(self, cache_key=None, cache_timeout=86400, category_id=None):
        if cache_key is not None:
            tree = cache.get(cache_key)

        # build tree
        if tree is None:
            tree = self._get_tree(self._get_root_categories())
            if cache_key is not None:
                cache.set(cache_key, tree, cache_timeout)

        # create output
        current = self._find_node(tree, category_id) if category_id else None
        output = {
            'tree': tree,
            'current': current,
            'ancestors': self._find_ancestors(tree, [], current['parent'] if current else None)
        }

        return output

    def _find_ancestors(self, tree, ancestors, id):
        if id is not None:
            curr = self._find_node(tree, id)
            del curr['children']
            if curr is not None:
                ancestors.append(curr)
                if curr['parent'] is not None:
                    ancestors = self._find_ancestors(tree, ancestors, curr['parent'])

        return ancestors

    def _find_node(self, tree, id):
        for c in tree:
            if id == c['id']:
                return c
            else:
                res = self._find_node(c['children'], id)
                if res is not None:
                    return res

    def _get_root_categories(self):
        tree = []
        categories = ProductCategory \
                        .objects \
                        .filter(active_flag=True) \
                        .order_by('name')
        for c in categories:
            if c.is_root_node():
                tree.append(c)

        return tree

    def _get_tree(self, categories):
        output = []

        for c in categories:
            count = self._get_product_count(c)
            if self.populated_categories_only and count == 0:
                continue

            children = self._get_tree(
                c.get_children().filter(active_flag=True)
            )

            output.append({
                'id': c.id,
                'children': children,
                'image': image_path(c.image),
                'name': c.name,
                'parent': c.parent.id if c.parent else None,
                'product_count': count,
                'short_name': c.short_name,
                'slug': c.slug,
                'slug_path': c.slug_path,
            })

        return output

    def _get_product_count(self, category):
        ids = category \
                .get_descendants(include_self=True) \
                .values_list('id', flat=True)

        pv = ProductVariant \
                .objects \
                .filter(product__category__id__in=list(ids)) \
                .filter(product__active_flag=True) \
                .filter(active_flag=True) \
                .filter(available_on_ecom=True) \

        if len(self.product_attributes_include) > 0:
            # pv = pv.filter()
            pass

        if len(self.product_attributes_exclude) > 0:
            # pv = pv.exclude()
            pass

        if len(self.variant_attributes_include) > 0:
            # pv = pv.filter()
            pass

        if len(self.variant_attributes_exclude) > 0:
            # pv = pv.exclude()
            pass

        return pv \
                .order_by('product__id') \
                .distinct('product__id') \
                .count()

    def product_attributes_include(self, include_list):
        self.product_attributes_include = include_list

    def product_attributes_exclude(self, exclude_list):
        self.product_attributes_exclude = exclude_list

    def variant_attributes_include(self, include_list):
        self.variant_attributes_include = include_list

    def variant_attributes_exclude(self, exclude_list):
        self.variant_attributes_exclude = exclude_list
