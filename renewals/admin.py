from django.contrib import admin
from django.core.mail import send_mail
from .models import CustomUser
from django.conf import settings

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_active', 'is_approved']
    list_filter = ['is_active', 'is_approved']
    actions = ['approve_users']

    def approve_users(self, request, queryset):
        queryset.update(is_active=True)  # Set to active once approved
        for user in queryset:
            send_mail(
                'Account Approved',
                f'Hi {user.username}, your account has been approved. You can now log in.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

    approve_users.short_description = 'Approve selected users'

admin.site.register(CustomUser, CustomUserAdmin)
