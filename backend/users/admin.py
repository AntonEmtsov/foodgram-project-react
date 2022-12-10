from django.contrib import admin

from .models import Subscribe, User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
    )
    search_fields = ('username',)
    list_filter = ('is_superuser',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'following')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = '-пусто-'
