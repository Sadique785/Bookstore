from django.contrib import admin
from .models import *
# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'category_image', 'order', 'description')
    search_fields = ('category_name', 'category_name')

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory)


class CouponAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'is_expired', 'discount_price', 'minimum_amount')
    search_fields = ('coupon_code', 'is_expired')

admin.site.register(Coupon, CouponAdmin)







class ProductImageAdmin(admin.StackedInline):
    model = ProductImage

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'category', 'product_description')
    inlines = [ProductImageAdmin]

@admin.register(LanguageVariant)
class LanguageVariantAdminn(admin.ModelAdmin):
    list_display = ['name', 'price']
    model = LanguageVariant

@admin.register(EditionVariant)
class EditionVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    model = EditionVariant








class AudiobookAdmin(admin.ModelAdmin):
    list_display = ('product', 'audio_link', 'duration')

class EbookAdmin(admin.ModelAdmin):
    list_display = ('product', 'ebook_file')

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('product_name', 'category', 'sub_category', 'has_audiobook')  

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'bio')  
    search_fields = ('name',)  
    inlines = [ProductInline] 

admin.site.register(Author, AuthorAdmin)

admin.site.register(Product, ProductAdmin)
admin.site.register(Audiobook, AudiobookAdmin)
admin.site.register(Ebook, EbookAdmin)

