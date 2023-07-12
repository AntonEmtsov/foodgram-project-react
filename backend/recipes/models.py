"""Модели для приложения recipes."""
from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram import settings

User = get_user_model()

MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH = 'Минимальное значение 1 минута!'
MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH = 'Выберете хотя бы 1 ингредиент.'


def image_recipe_upload_user_folder(instance, filename):
    return 'recipes/recipe_images/user_id_{0}/{1}'.format(instance.author.id, filename)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Название ингредиента',
    )
    measurement_unit = models.CharField(
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class IngredientQuantity(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    current_recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=[
            MinValueValidator(
                settings.INGREDIENT_IN_RECIPE_MIN_LENGTH,
                message=MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH,
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        default_related_name = 'ingridientsquantity'
        constraints = (
            models.UniqueConstraint(
                fields=('current_recipe', 'ingredient',),
                name='Единственность ингредиента в рецепте',
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=1),
                name='amount_gte_1',
            ),
        )

    def __str__(self):
        return f'{self.amount} {self.ingredient}'


class Tag(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Тег',
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        unique=True,
    )
    color = ColorField(
        unique=True,
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        default='#FF0000',
        format='hex',
        verbose_name='Цвет',
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
        max_length=255,
        verbose_name='Название',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to=image_recipe_upload_user_folder,
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                settings.RECIPE_COOKING_TIME_MIN_LENGTH,
                message=MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH,
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
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
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
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite_user',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальность избранности рецепта',
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='cart_recipe',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Уникальность списка покупок',
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe} в списке у {self.user}'
