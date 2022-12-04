from django.core.validators import MinValueValidator
from django.db import models
from colorfield.fields import ColorField

from foodgram import settings
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица Измерения',
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        max_length=settings.TAG_SLUG_MAX_LENGTH,
        unique=True,
    )
    color = ColorField(
        verbose_name='Цвет',
        default='#FF0000',
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.RECIPE_NAME_MAX_LENGTH
    )
    image = models.ImageField(
        'Картинк',
        upload_to='recipes/images/'
    )
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientsInRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.RECIPE_COOKING_TIME_MIN_LENGTH,
                message='Минимальное значение 1 минута!',
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientsInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                settings.INGREDIENT_IN_RECIPE_MIN_LENGTH,
                message='Выберете хотя бы 1 ингредиент.',
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return (f'{self.ingredient.name} - {self.amount}'
                f' {self.ingredient.measurement_unit}')


class UserFavoriteRecipes(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
