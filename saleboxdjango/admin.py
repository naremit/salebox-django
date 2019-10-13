from django.contrib import admin
from saleboxdjango.models import *


class CheckoutStoreUpdateInline(admin.TabularInline):
    model = CheckoutStoreUpdate
    readonly_fields = ('status', 'created', 'data')
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

class DiscountRulesetInline(admin.TabularInline):
    model = DiscountRuleset
    exclude = ['product_variant']
    extra = 0


class AttributeAdmin(admin.ModelAdmin):
    list_display = ('code',)


class AttributeItemAdmin(admin.ModelAdmin):
    list_display = ('value', 'slug', 'attribute')
    list_filter = ('attribute',)


class BasketWishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session', 'variant', 'quantity', 'weight', 'basket_flag')
    list_filter = ('basket_flag',)
    search_fields = ('user__email',)


class CallbackStoreAdmin(admin.ModelAdmin):
    list_display = ('created', 'ip_address', 'method')
    search_fields = ('post',)


class CheckoutStoreAdmin(admin.ModelAdmin):
    list_display = ('created', 'status', 'uuid', 'visible_id', 'user', 'gateway_code')
    inlines = [CheckoutStoreUpdateInline]
    list_filter = ('status', 'gateway_code')
    readonly_fields = ('uuid', 'visible_id', 'user', 'gateway_code', 'status', 'data', 'payment_received')
    search_fields = ('visible_id', 'data')


class CountryAdmin(admin.ModelAdmin):
    list_display = ('code', 'default')


class CountryStateAdmin(admin.ModelAdmin):
    list_display = ('country', 'code', 'full_code')


class DiscountGroupAdmin(admin.ModelAdmin):
    inlines = [DiscountRulesetInline]
    list_display = ('name', 'group_type')
    list_filter = ('group_type',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('event', 'salebox_member_id', 'transaction_guid', 'processed_flag', 'created')
    list_filter = ('event', 'processed_flag')
    readonly_fields = ('event', 'salebox_member_id', 'transaction_guid', 'created')
    search_fields = ('salebox_member_id', 'transaction_guid')


class LastUpdateAdmin(admin.ModelAdmin):
    list_display = ('code', 'value')


class MemberGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'flat_discount_percentage')


class MemberAdmin(admin.ModelAdmin):
    list_display = ('guid', 'email', 'name_first', 'name_last', 'group')
    list_filter = ('group',)
    readonly_fields = ('parent',)
    search_fields = ('guid', 'email')


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug_path')
    search_fields = ('name', 'slug_path')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'sold_by', 'slug')
    list_filter = ('sold_by', 'category')
    search_fields = ('name', 'slug', 'plu', 'sku')


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'price', 'slug')
    list_filter = ('product__category',)


class ProductVariantRatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'variant', 'rating', 'created')
    search_fields = ('user__email',)


class TranslationAdmin(admin.ModelAdmin):
    list_display = ('language_code', 'key', 'value')
    list_filter = ('language_code',)
    search_fields = ('key',)

class UserAddressAdmin(admin.ModelAdmin):
    list_display = (
        'address_group',
        'user',
        'full_name',
        'address_1',
        'address_2',
        'country_state',
        'country',
        'postcode'
    )
    list_filter = ('address_group',)
    search_fields = (
        'user__email',
        'full_name',
        'address_1',
        'address_2',
        'address_3',
        'postcode'
    )


admin.site.register(Attribute, AttributeAdmin)
admin.site.register(AttributeItem, AttributeItemAdmin)
admin.site.register(BasketWishlist, BasketWishlistAdmin)
admin.site.register(CallbackStore, CallbackStoreAdmin)
admin.site.register(CheckoutStore, CheckoutStoreAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(CountryState, CountryStateAdmin)
admin.site.register(DiscountGroup, DiscountGroupAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(LastUpdate, LastUpdateAdmin)
admin.site.register(MemberGroup, MemberGroupAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductVariantRating, ProductVariantRatingAdmin)
admin.site.register(Translation, TranslationAdmin)
admin.site.register(UserAddress, UserAddressAdmin)
