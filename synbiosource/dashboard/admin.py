from django.contrib import admin
from .models import AllUsers
from django.contrib.auth.admin import UserAdmin
# Register your models here.

class UserConfig(UserAdmin):
    """Class to style the appearance of the admin dashboard."""
    model = AllUsers
    search_fields = ('email', 'full_name',)
    list_filter = ('email','full_name', 'is_active', 'is_staff')
    ordering = ('-start_at',)
    list_display = ('email', 'full_name',
                    'is_active', 'is_staff','is_moderator')
    fieldsets = (
        (None, {'fields': ('email', 'full_name','password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active','is_superuser','is_moderator','user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name','email','password1', 'password2', 'is_active', 'is_staff','is_moderator','user_permissions')}
        ),
    )


admin.site.register(AllUsers, UserConfig)