from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.html import format_html

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type_badge', 'is_superuser_badge', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'groups', 'user_type', 'is_superuser')
    ordering = ('username',)
    fieldsets = (
        ('Login Info', {
            'fields': ('username', 'password'),
            'description': 'User login credentials.'
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email'),
            'description': 'User contact details.'
        }),
        ('Permissions', {
            'fields': ('is_active', 'groups', 'user_type', 'is_superuser'),
            'description': 'User roles and permissions.'
        }),
    )
    def user_type_badge(self, obj):
        color = {
            'user': 'gray',
            'manager': 'blue',
            'admin': 'orange',
        }.get(obj.user_type, 'black')
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:8px;font-size:0.9em;">{}</span>', color, obj.get_user_type_display())
    user_type_badge.short_description = 'Role'
    def is_superuser_badge(self, obj):
        if obj.is_superuser:
            return format_html('<span style="background:purple;color:white;padding:2px 8px;border-radius:8px;font-size:0.9em;">Superadmin</span>')
        return ''
    is_superuser_badge.short_description = 'Superadmin'
