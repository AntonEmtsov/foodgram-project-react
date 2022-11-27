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
    pass


class IngredientsInRecipe(models.Model):
    pass


class Tags(models.Model):
    pass


class UsersFavoriteRecipes(models.Model):
    pass


class ShoppingList(models.Model):
    pass
