from django.contrib import admin
from saleboxecomdjango.models import *


class DiscountRulesetInline(admin.TabularInline):
    model = DiscountRuleset
    exclude = ['product_variant']
    extra = 0


class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    extra = 0


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('code',)


class AttributeItemAdmin(admin.ModelAdmin):
    list_display = ('value', 'slug', 'attribute')
    list_filter = ('attribute',)


class DiscountGroupAdmin(admin.ModelAdmin):
    inlines = [DiscountRulesetInline]
    list_display = ('name', 'group_type')
    list_filter = ('group_type',)


class LastUpdateAdmin(admin.ModelAdmin):
    list_display = ('code', 'value')


class MemberGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'flat_discount_percentage')


class MemberAdmin(admin.ModelAdmin):
    list_display = ('guid', 'name_first', 'name_last', 'group')
    list_filter = ('group',)


class ProductCategoryAdmin(admin.ModelAdmin):
    pass


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sold_by')
    list_filter = ('sold_by', 'category')
    list_editable = ('sold_by',)
    search_fields = ('name',)


admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeItem, AttributeItemAdmin)
admin.site.register(DiscountGroup, DiscountGroupAdmin)
admin.site.register(LastUpdate, LastUpdateAdmin)
admin.site.register(MemberGroup, MemberGroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
