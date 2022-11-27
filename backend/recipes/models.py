from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    image = models.ImageField(
        'Картинк',
        upload_to='recipes/images/'
    )
    text = models.TextField('Описание')
    ingredients = ...
    tags = ...
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(
            1,
            message='Минимальное значение 1 минута!',
        )]
    )


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица Измерения'
    )


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Byuhtlbtyn',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
    )


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=200,
    )
    color = models.CharField(
        verbose_name='Цвет',
    )


class UserFavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт'
    )


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт'
    )
