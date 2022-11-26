from django.contrib import admin

from .models import User, Follow


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'username', 'email',)
    search_fields = ('username', 'role',)
    list_filter = ('role', 'is_superuser',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = '-пусто-'
