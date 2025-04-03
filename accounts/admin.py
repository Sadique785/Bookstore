from django.contrib import admin
from .models import Profile, Cart, CartItem, Wallet, Transaction, Invoice
# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'is_email_verified', 'profile_image', 'mobile')

    def user_email(self, obj):
        return obj.user.email if obj.user else ''

    user_email.short_description = 'User Email'

admin.site.register(Profile, ProfileAdmin)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_paid')
    list_filter = ('is_paid',)
    search_fields = ('user__username', 'user__email')

class CartItemAdmin(admin.ModelAdmin):
    list_display = ( 'cart', 'product', 'language_variant', 'edition_variant')
    search_fields = ('cart__user__username', 'product__product_name')

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'description', 'timestamp')


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'order_item')
    search_fields = ('name', 'order_item__some_field')  

admin.site.register(Invoice, InvoiceAdmin)