from django.contrib import admin

from .models import User


@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'role', 'username', 'email',)
    search_fields = ('username', 'role',)
    list_filter = ('role', 'is_superuser',)
    empty_value_display = '-пусто-'
