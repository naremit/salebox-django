from django.shortcuts import redirect

from django.views.generic import TemplateView

from saleboxdjango.lib.category import SaleboxCategory
from saleboxdjango.lib.product import SaleboxProduct
from saleboxdjango.models import ProductCategory, ProductVariant


class SaleboxProductsView(TemplateView):
    page_number = 1
    path = []


    def dispatch(self, request, *args, **kwargs):
        # retrieve our url path
        self.path = self.kwargs['path'].strip('/').split('/')
        self.path = [p.strip() for p in self.path if len(p.strip()) > 0]

        # retrieve page number
        if len(self.path) > 0:
            if self._is_positive_integer(self.path[-1]):
                self.page_number = int(self.path[-1])
                self.path.pop()

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if len(self.path) == 0:
            return self.product_list(None, request, *args, **kwargs)

        # is this a product?
        if len(self.path) == 2 and self.path[0] == 'product':
            id = int(self.path[-1].split('-')[0])
            pv = ProductVariant.objects.filter(active_flag=True).filter(id=id).first()
            return self.product_detail(pv, request, *args, **kwargs)

        # this is a category
        pc = ProductCategory.objects.filter(active_flag=True).filter(slug=self.path[-1]).first()
        if pc:
            return self.product_list(pc, request, *args, **kwargs)

        # go up a level
        return redirect('/')


    def product_detail(self, variant, request, *args, **kwargs):
        self.template_name = 'salebox/product/product_detail.html'

        #
        context = self.get_context_data(**kwargs)
        context['variant'] = variant

        # render
        return self.render_to_response(context)

    def product_list(self, category, request, *args, **kwargs):
        self.template_name = 'salebox/product/product_list.html'
        context = self.get_context_data(**kwargs)

        # fetch categories
        sc = SaleboxCategory()
        context['categories'] = sc.get_tree(
            cache_key='product_categories',
            category_id=category.id if category else None
        )

        # fetch products
        sp = SaleboxProduct()
        pagination_suffix = ''
        if len(self.path) > 0:
            pagination_suffix = '%s/' % '/'.join(self.path)
        sp.set_pagination(self.page_number, 20, '/en/shop/%s' % pagination_suffix)
        if category:
            sp.set_category(category)
        context['products'] = sp.get_list()

        # render
        return self.render_to_response(context)

    def _is_positive_integer(self, value):
        try:
            i = int(value)
            if i > 0:
                return True
        except:
            pass

        return False