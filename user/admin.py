from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "name", "surname", "is_staff")
    search_fields = ("email", "name", "surname")
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "name",
                    "surname",
                    "avatar",
                    "phone",
                    "github_url",
                    "about",
                ),
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            "Дополнительная информация",
            {
                "fields": (
                    "email",
                    "name",
                    "surname",
                ),
            },
        ),
    )
