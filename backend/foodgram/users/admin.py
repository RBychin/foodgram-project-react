from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email']

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        if request.user.is_superuser:
            return super().get_fieldsets(request, obj)
        return (
            ('Основная информация',
             {"fields": ("username",
                         "email",
                         "password")}
             ),
            (_("Personal info"),
             {"fields": ("first_name",
                         "last_name")}
             ),
            (
                _("Permissions"),
                {
                    "fields": (
                        "is_active",
                    ),
                },
            ))

    def get_readonly_fields(self, request, obj=None):
        if obj is None:
            return self.readonly_fields
        if not request.user.is_superuser and obj.is_superuser:
            return [
                'username',
                'email',
                'password',
                'first_name',
                'last_name',
                'is_active'
            ]
        return self.readonly_fields
