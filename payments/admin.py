from django.contrib import admin
from .models import PaymentMethod

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

admin.site.register(PaymentMethod, PaymentMethodAdmin)


# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('amount', 'payment_method', 'order', 'payment_status', 'created_at', 'updated_at')
#     list_filter = ('payment_status', 'created_at', 'updated_at')
#     search_fields = ('amount', 'payment_method__name', 'order__order_id')  # Adjust the fields as needed

# admin.site.register(Payment, PaymentAdmin)

