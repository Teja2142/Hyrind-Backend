from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email', 'role', 'approval_status', 'portal_access', 'is_staff', 'created_at')
    list_filter   = ('role', 'approval_status', 'portal_access', 'is_staff')
    search_fields = ('email',)
    ordering      = ('-created_at',)
    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Role & Status', {'fields': ('role', 'approval_status', 'portal_access')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display  = ('full_name', 'user', 'phone', 'visa_status', 'created_at')
    search_fields = ('first_name', 'last_name', 'user__email')
    raw_id_fields = ('user',)
