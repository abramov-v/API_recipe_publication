from django.contrib import admin

from users.models import User


@admin.register(User)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_display_links = ('username',)
    empty_value_display = '-пусто-'
