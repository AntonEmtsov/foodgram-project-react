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
                            ShoppingList, Tag, UserFavoriteRecipe)
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

    def create_object(self, request, pk, serializers):
        serializer = serializers(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_object(self, request, pk, model):
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk),
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        return self.create_object(request, pk, FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.delete_object(request, pk, UserFavoriteRecipe)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        return self.create_object(request, pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.delete_object(request, pk, ShoppingList)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(IsAuthenticated, ),
    )
    def download_shopping_cart(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = IngredientsInRecipe.objects.filter(
            id__in=request.user.shopping_cart.values_list(
                'recipe__id',
                flat=True,
            )
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'ingredient_amount',
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = (
            'attachment;'
            'filename="Shoppingcart.csv"'
        )
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response
