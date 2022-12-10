import csv

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientFilter, RecipesFilter
from .mixins import CreateDestroyViewSet
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipeEditSerializer, RecipeReadSerializer,
                          SetPasswordSerializer, ShoppingCartSerializer,
                          SubscribeSerializer, TagSerializer,
                          UserCreateSerializer, UserListSerializer)
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscribe

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'create':
            return UserCreateSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = Subscribe.objects.filter(user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request},)
        return self.get_paginated_response(serializer.data)


class SubscribeViewSet(CreateDestroyViewSet):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['author_id'] = self.kwargs.get('user_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            author=get_object_or_404(
                User,
                id=self.kwargs.get('user_id')
            )
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeEditSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=False,
        methods=('get',),
        url_path='download_shopping_cart',
        pagination_class=None)
    def download_file(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                'Нет списка покупок', status=status.HTTP_400_BAD_REQUEST)
        shopping_cart = user.shopping_cart.select_related('recipe').values(
            'recipe__recipe__ingredient__name',
            'recipe__recipe__ingredient__measurement_unit'
        ).annotate(Sum('recipe__recipe__amount')).order_by(
            'recipe__recipe__ingredient__name'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment;'
            'filename="Shoppingcart.csv"'
        )
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(shopping_cart):
            writer.writerow(item)
        return response

    @action(methods=('delete',), detail=True)
    def delete(self, request, user_id):
        get_object_or_404(User, id=user_id)
        if not Subscribe.objects.filter(
                user=request.user, author_id=user_id).exists():
            return Response({'errors': 'Вы не были подписаны на автора'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            Subscribe,
            user=request.user,
            author_id=user_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteRecipeViewSet(CreateDestroyViewSet):
    serializer_class = FavoriteRecipeSerializer

    def get_queryset(self):
        user = self.request.user.id
        return FavoriteRecipe.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            favorite_recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        u = request.user
        if not u.favorite.select_related(
                'favorite_recipe').filter(
                    favorite_recipe_id=recipe_id).exists():
            return Response({'errors': 'Рецепт не в избранном'},
                            status=status.HTTP_400_BAD_REQUEST)
        get_object_or_404(
            FavoriteRecipe,
            user=request.user,
            favorite_recipe_id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateDestroyViewSet):
    serializer_class = ShoppingCartSerializer

    def get_queryset(self):
        user = self.request.user.id
        return ShoppingCart.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['recipe_id'] = self.kwargs.get('recipe_id')
        return context

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=self.kwargs.get('recipe_id')
            )
        )

    @action(methods=('delete',), detail=True)
    def delete(self, request, recipe_id):
        user = request.user
        if not user.shopping_cart.select_related(
            'recipe'
        ).filter(recipe_id=recipe_id).exists():
            return Response(
                {'errors': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
