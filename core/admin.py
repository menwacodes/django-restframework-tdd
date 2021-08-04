from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# translation not used per se but Django can support many languages
from django.utils.translation import gettext as _

from core import models


# custom user admin
class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

admin.site.register(models.User, UserAdmin)
