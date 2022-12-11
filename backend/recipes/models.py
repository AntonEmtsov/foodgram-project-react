"""Модели для приложения recipes."""
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=1000,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=1000,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='Ингредиент'
    )
    current_recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(1, message='Количество не может быть меньше 1!')
        ]
    )

    class Meta:
        default_related_name = 'ingridientsquantity'
        constraints = (
            models.UniqueConstraint(
                fields=('current_recipe', 'ingredient',),
                name='recipe_ingredient_exists'),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1'),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Тег рецепта',
    )
    slug = models.SlugField(
        verbose_name='Уникальное название тега',
        unique=True
    )
    color = ColorField(
        unique=True,
        max_length=7,
        default='#FF0000',
        format='hex',
        verbose_name='Цвет',
    )

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name=('Автор рецепта'),
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/media/',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1 мин.'
            )
        ]
    )

    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        IngredientQuantity,
        symmetrical=False,
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        ordering = ('name', )
        constraints = (
            models.UniqueConstraint(
                fields=('name',),
                name='recipe_name_exists'),
        )

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='favorite_user_recept_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='cart_recipe'
    )

    class Meta:
        verbose_name = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='Shopping_cart_recept_unique'
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке у {self.user}'
