from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'email',
        'first_name',
        'is_active',
        'date_joined',
    )
    ordering = ('username',)
