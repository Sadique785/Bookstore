from django.contrib import admin
from .models import PaymentMethod

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

admin.site.register(PaymentMethod, PaymentMethodAdmin)



