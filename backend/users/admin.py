from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'role', 'username', 'email', 'first_name', 'last_name',
    )
    search_fields = ('username', 'role', 'first_name', 'last_name')
    list_filter = ('role', 'is_superuser',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'user', 'created'
    )
    search_fields = ('author', 'created')
    list_filter = ('author', 'user', 'created')
    empy_value_display = '-пусто-'
