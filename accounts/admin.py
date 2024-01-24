from django.contrib import admin
from .models import Profile
# Register your models here.


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'is_email_verified', 'profile_image', 'mobile')

    def user_email(self, obj):
        return obj.user.email if obj.user else ''

    user_email.short_description = 'User Email'

admin.site.register(Profile, ProfileAdmin)