from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from foodgram import settings

User = get_user_model()

MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH = 'Минимальное значение 1 минута!'
MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH = 'Выберете хотя бы 1 ингредиент.'


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.INGREDIENT_NAME_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=settings.INGREDIENT_MEASUREMENT_UNIT_MAX_LENGTH
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique name measurement'
            ),
        )

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=settings.TAG_NAME_MAX_LENGTH,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=settings.TAG_COLOR_MAX_LENGTH,
        default='#00ff7f',
        null=True,
        blank=True,
        unique=True,
    )
    slug = models.SlugField(
        'Ссылка',
        max_length=settings.TAG_SLUG_MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/images',
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=settings.RECIPE_NAME_MAX_LENGTH,
    )
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        default=1,
        validators=[
            MinValueValidator(
                settings.RECIPE_COOKING_TIME_MIN_LENGTH,
                message=MESSAGE_RECIPE_COOKING_TIME_MIN_LENGTH,
            )
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'Автор: {self.author.username} рецепт: {self.name}'


class IngredientAmount(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='recipe',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient',
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1,
        validators=[
            MinValueValidator(
                settings.INGREDIENT_IN_RECIPE_MIN_LENGTH,
                message=MESSAGE_INGREDIENT_IN_RECIPE_MIN_LENGTH,
            )
        ]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='Единственность ингредиента в рецепте',
            ),
        )

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='favorite',

    )
    favorite_recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Избранный'
        verbose_name_plural = 'Избранные'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'favorite_recipe'),
                name='Уникальность избранности рецепта',
            ),
        )

    def __str__(self):
        return (f'Пользователь: {self.user.username}'
                f'рецепт: {self.favorite_recipe.name}')


class ShoppingCart(models.Model):
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
        related_name='recipe_shopping_cart',
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='Уникальность списка покупок',
            ),
        )

    def __str__(self):
        return (f'Пользователь: {self.user.username},'
                f'Рецепт в списке: {self.recipe.name}')
