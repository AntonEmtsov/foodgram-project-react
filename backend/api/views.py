import csv

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .mixins import RetrieveListViewSet
from .permissions import IsAuthorOrStaffOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeListSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer, UserApiSerializer)
from recipes.models import (Ingredient, IngredientsInRecipe, Recipe,
                            ShoppingList, Tag, UserFavoriteRecipes)
from users.models import Follow, User


class UsersApiViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserApiSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'Ошибка подписки. Нельзя подписываться на себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(user=user, author=author).exists():
            return Response(
                {
                    'errors':
                    'Ошибка подписки. Вы уже подписаны на пользователя!'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            SubscribeSerializer(
                Follow.objects.create(user=user, author=author),
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            SubscribeSerializer(
                self.paginate_queryset(
                    Follow.objects.filter(user=request.user)
                ),
                many=True,
                context={'request': request},
            ).data
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors':
                    'Ошибка отписки. Нельзя отписаться от себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        follow = Follow.objects.filter(user=user, author=author)
        if not follow.exists():
            return Response(
                {'errors': 'Ошибка отписки. Вы не подписаны'},
                status=status.HTTP_400_BAD_REQUEST)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(RetrieveListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


class IngredientsViewSet(RetrieveListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    permission_classes = (IsAuthorOrStaffOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(
        methods=['get', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        favorite = UserFavoriteRecipes.objects.filter(
            user=user,
            recipe=recipe,
        )
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'GET':
            if not favorite:
                favorite = UserFavoriteRecipes.objects.create(
                    user=user,
                    recipe=recipe
                )
                return Response(
                    data=FavoriteSerializer(favorite.recipe).data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if not favorite:
                return Response(
                    {'errors': 'Такого рецепта нет в избранных.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
    )
    def shopping_cart(self, request, pk=None):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        in_shopping_cart = ShoppingList.objects.filter(
            user=user,
            recipe=recipe
        )
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if not in_shopping_cart:
                shopping_cart = ShoppingList.objects.create(
                    user=user,
                    recipe=recipe
                )
                return Response(
                    data=ShoppingCartSerializer(shopping_cart.recipe).data,
                    status=status.HTTP_201_CREATED
                )
        elif request.method == 'DELETE':
            if not in_shopping_cart:
                return Response(
                    {'errors': 'Такого рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            in_shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientsInRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_amount'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment;'
            'filename="Shoppingcart.csv"'
        )
        response.write(u'\ufeff'.encode('utf8'))
        for item in list(ingredients):
            csv.writer(response).writerow(item)
        return response
