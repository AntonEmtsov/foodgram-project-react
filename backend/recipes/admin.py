from django.contrib import admin

from .models import (Ingredient, IngredientsInRecipe, Recipe, ShoppingList,
                     Tag, UserFavoriteRecipes)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientsInRecipe


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('measurement_unit',)
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'name', 'image', 'text',
        'cooking_time', 'pub_date', 'favorited',
    )
    search_fields = ('author', 'name', 'tags')
    list_filter = ('tags',)
    inlines = (IngredientRecipeInline,)
    empty_value_display = '-пусто-'

    def favorited(self, obj):
        return UserFavoriteRecipes.objects.filter(recipe=obj).count()


@admin.register(UserFavoriteRecipes)
class UserFavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
