from django.contrib import admin

# Register your models here.
from .models import Order, OrderAddress, OrderPayment, OrderItem




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_status', 'total_amount')
    search_fields = ('user__username', 'order_status')



@admin.register(OrderAddress)
class OrderAddressAdmin(admin.ModelAdmin):
    list_display = ('order', 'name', 'city', 'country', 'state', 'postal_code', 'street_address', 'mobile', 'email')
    list_filter = ('is_billing_address', 'is_shipping_address')
    search_fields = ('order__user__username', 'name', 'city', 'state', 'postal_code')

@admin.register(OrderPayment)
class OrderPaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method')
    search_fields = ('order__user__username', 'payment_method__name')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('uid', 'order', 'product_name', 'quantity', 'price', 'order_status', 'is_active', 'is_delivered')
    list_filter = ('order_status', 'is_active', 'is_delivered')
    search_fields = ('product_name', 'order__uid', 'name', 'mobile')



# admin.site.register(OrderAdmin, OrderAddressAdmin, OrderPaymentAdmin)