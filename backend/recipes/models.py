from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH = 'Минимальное значение 1 минута!'
MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH = 'Выберете хотя бы 1 ингредиент.'


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200
    )
    color = ColorField(
        verbose_name='Цвет тега',
        default='#FF0000',
    )
    slug = models.SlugField(
        verbose_name='Ссылка',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название Ингредиенты',
        max_length=144,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=144,
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        related_name='recipes',
        through='RecipeIngredient'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='media/image/',
        verbose_name='Изображение рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготавления',
        validators=[
            MinValueValidator(
                1,
                message=MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH,
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


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов',
        validators=[
            MinValueValidator(
                1,
                message=MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH,
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Единственность ингредиента в рецепте',
            ),
        )

    def __str__(self):
        return f'{self.ingredient}, {self.recipe}'


class Purchase(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='purchase'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='purchase'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальность списка покупок',
            ),
        )

    def __str__(self):
        return f'В корзине {self.user} есть {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite'
    )

    class Meta:
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальность избранности рецепта',
            ),
        )

    def __str__(self):
        return f'{self.user}, {self.recipe}'
