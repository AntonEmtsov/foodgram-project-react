from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import CustomPagination
from .serializers import (CreateUpdateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          ShoppingCartSerializer, SubscribeCreateSerializer,
                          SubscribeSerializer, TagSerializer)
from recipes.models import (Favorite, Ingredient, IngredientQuantity, Recipe,
                            ShoppingCart, Tag, User)
from users.models import Subscribe


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = SubscribeSerializer

    @action(
        detail=True,
        methods=('post',),
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        if user == author:
            return Response({
                'errors': 'Нельзя подписываться на себя.'
            }, status=status.HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(following=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на пользователя'
            }, status=status.HTTP_400_BAD_REQUEST)
        subscribe = Subscribe.objects.create(following=user, author=author)
        serializer = SubscribeCreateSerializer(
            subscribe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        user = request.user
        author = get_object_or_404(User, id=pk)
        subscribe = get_object_or_404(
            Subscribe, following=user, author=author
        )
        subscribe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        result = self.paginate_queryset(
            User.objects.filter(
                following__following=request.user
            )
        )
        serializer = SubscribeSerializer(
            result, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    pagination_class = None
    serializer_class = IngredientSerializer
    filterset_class = IngredientSearchFilter
    search_fields = ('^name',)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    pagination_class = None
    serializer_class = TagSerializer
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filterset_class = RecipeFilter
    search_fields = ('=name',)

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH'):
            return CreateUpdateRecipeSerializer
        return ListRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def recipe_post_method(self, request, anyserializer, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = anyserializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def recipe_delete_method(self, request, anymodel, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            anymodel, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', ],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk=None):
        return self.recipe_post_method(request, FavoriteSerializer, pk)

    @favorite.mapping.delete
    def delete_from_favorite(self, request, pk=None):
        return self.recipe_delete_method(request, Favorite, pk)

    @action(
        detail=True, methods=['post', ],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk=None):
        return self.recipe_post_method(request, ShoppingCartSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_from_shopping_card(self, request, pk=None):
        return self.recipe_delete_method(request, ShoppingCart, pk)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        shopping_cart = IngredientQuantity.objects.filter(
            current_recipe__cart_recipe__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        text = 'Cписок покупок: \n'
        for ingredients in shopping_cart:
            name, measurement_unit, amount = ingredients
            text += f'{name}: {amount} {measurement_unit}\n'
        response = HttpResponse(text, content_type='text/plain')
        filename = 'shoping_list.pdf'
        response['Content-Disposition'] = (
            f'attachment; filename={filename}'
        )
        return response
