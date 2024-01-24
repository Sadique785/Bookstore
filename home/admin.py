from django.contrib import admin
from .models import Address, UserAddress

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'street_address', 'city', 'state', 'postal_code', 'country', 'mobile', 'landmark')

@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'is_default')
    list_filter = ('is_default',)
    search_fields = ('user__username', 'address__street_address', 'address__city', 'address__state', 'address__postal_code', 'address__country')