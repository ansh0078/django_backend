from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Gives HR/admin a working Django Admin panel out of the box:
    view all users, edit, delete, promote to staff - satisfies the
    'Admin Dashboard: view all users, delete users' bonus requirement
    even before the React admin panel exists.
    """
    ordering = ["-created_at"]
    list_display = ["email", "name", "is_admin_user", "is_staff", "is_active", "created_at"]
    list_filter = ["is_admin_user", "is_staff", "is_active"]
    search_fields = ["email", "name"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name",)}),
        ("Permissions", {"fields": ("is_admin_user", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "name", "password1", "password2", "is_staff", "is_active"),
        }),
    )
    readonly_fields = ["created_at"]
