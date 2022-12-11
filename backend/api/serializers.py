from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from recipes.models import (Favorite, Ingredient, IngredientQuantity, Recipe,
                            ShoppingCart, Tag, User)
from users.models import Subscribe


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'first_name',
            'last_name', 'username', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            following=request.user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class TagListSerializer(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except ObjectDoesNotExist as e:
            raise serializers.ValidationError(
                'Объект не существует.'
            ) from e


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientQuantitySerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = IngredientQuantity
        fields = (
            'id',
            'amount',
        )

    def validate_quantity(self, data):
        if int(data) < 1:
            raise ValidationError({
                'ingredients': (
                    'Должно быть не менее одного ингредиента'
                ),
                'msg': data
            })
        return data

    def create(self, validated_data):
        return IngredientQuantity.objects.create(
            ingredient=validated_data.get('id'),
            amount=validated_data.get('amount')
        )


class IngredientQuantityShowSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='measurement_unit',
        read_only=True,
    )
    name = serializers.SlugRelatedField(
        source='ingredient',
        slug_field='name',
        read_only=True,
    )

    class Meta:
        model = IngredientQuantity
        fields = (
            'id', 'name', 'measurement_unit', 'amount',
        )


class ListRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        read_only=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image',
            'name', 'text', 'cooking_time', 'is_favorited',
            'is_in_shopping_cart',
        )

    @staticmethod
    def get_ingredients(obj):
        ingredients = IngredientQuantity.objects.filter(current_recipe=obj)
        return IngredientQuantityShowSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(use_url=True, max_length=None)
    author = UserSerializer(read_only=True)
    ingredients = IngredientQuantitySerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'image',
            'name', 'text', 'cooking_time',
        )

    @atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def create_ingredients(self, recipe, ingredients):
        IngredientQuantity.objects.bulk_create([
            IngredientQuantity(
                current_recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient['ingredient'],
            ) for ingredient in ingredients
        ])

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        print(data['ingredients'])
        ingredients = data
        if not ingredients:
            raise serializers.ValidationError(
                'Нужно выбрать хотябы 1 ингредиент!'
            )
        if data['cooking_time'] <= 0:
            raise ValidationError(
                'Минимум 1 минута'
            )
        return data

    @atomic
    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            recipe = instance
            ingredients = validated_data.pop('ingredients')
            IngredientQuantity.objects.filter(current_recipe=recipe).delete()
            self.create_ingredients(recipe, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return ListRecipeSerializer(
            instance,
            context={
                'request': self.context.get('request'),
            }
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='recipe.name')
    id = serializers.ReadOnlyField(source='recipe.id')

    class Meta:
        model = Favorite
        fields = ('name', 'id', 'user', 'recipe',)

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortShowSerializer(
            instance.recipe, context=context).data


class RecipeShortShowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('name', 'id', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count', 'is_subscribed'
        )

    def get_is_subscribed(self, obj: User):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(
            following=request.user, author=obj).exists()

    def get_recipes(self, author):
        queryset = self.context.get('request')
        recipes_limit = queryset.query_params.get('recipes_limit')
        if not recipes_limit:
            return RecipeShortShowSerializer(
                Recipe.objects.filter(author=author),
                many=True, context={'request': queryset}
            ).data
        return RecipeShortShowSerializer(
            Recipe.objects.filter(author=author)[:int(recipes_limit)],
            many=True,
            context={'request': queryset}
        ).data

    def get_recipes_count(self, author):
        return author.recipes.all().count()


class SubscribeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ('following', 'author')

    def validate(self, data):
        get_object_or_404(User, username=data['author'])
        if self.context['request'].following == data['author']:
            raise ValidationError({
                'errors': 'Нельзя подписаться на самого себя.'
            })
        if Subscribe.objects.filter(
                following=self.context['request'].following,
                author=data['author']
        ):
            raise ValidationError({
                'errors': 'Уже подписан.'
            })
        return data

    def to_representation(self, instance):
        """Метод вывода данных."""
        return SubscribeSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.ReadOnlyField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = ShoppingCart
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data['user'],
            recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError(
                'Рецепт уже в списке покупок.'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortShowSerializer(
            instance.recipe,
            context=context).data
