from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from djoser.views import UserViewSet
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    TagSerializer, IngredientSerializer, RecipeListSerializer,
    RecipeCreateSerializer, SubscriptionsSerializer,
    RecipeForSubscriptionSerializer
)
from recipes.models import (Recipe, Tag,
                            Ingredient, ShoppingCart,
                            RecipeIngredient, Favorite
                            )
from users.models import Subscription

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Viewset для работы с пользователями и подписками."""

    pagination_class = CustomPagination

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated]
            )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        authors = [subscription.author for subscription in subscriptions]
        page = self.paginate_queryset(authors)
        serializer = SubscriptionsSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
            )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)

        if request.user.id == author.id:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            try:
                Subscription.objects.create(user=request.user, author=author)
            except IntegrityError:
                return Response(
                    {'detail': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SubscriptionsSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscription.objects.filter(
                user=request.user,
                author=author
            )
            if subscription.exists():
                subscription.delete()
                return Response(
                    {'detail': 'Unsubscribed successfully.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'detail': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class TagViewSet(ReadOnlyModelViewSet):
    """Viwset для получения тегов."""

    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Viwset для получения ингредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(ModelViewSet):
    """Viewset дла работы с рецептами."""

    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'patch', 'partial_update'):
            return RecipeCreateSerializer
        return RecipeListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
            )
    def shopping_cart(self, request, pk):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'detail': 'Такой рецепт не существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Рецепт уже добавлен в список покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeForSubscriptionSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            shopping_cart_item = ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
            )
            if shopping_cart_item.exists():
                shopping_cart_item.delete()
                return Response(
                    {'detail': 'Рецепт удален из списка покупок.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'detail': 'Рецепт не найден в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get']
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__is_in_shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')
        shopping_cart_content = 'Список покупок:\n'
        for item in ingredients:
            shopping_cart_content += (
                f"\n* {item['ingredient__name']} "
                f"{(item['ingredient__measurement_unit'])} - "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(
            shopping_cart_content,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated]
            )
    def favorite(self, request, pk):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(pk=pk)
            except Recipe.DoesNotExist:
                return Response(
                    {'detail': 'Рецепт не существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeForSubscriptionSerializer(recipe)
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, pk=pk)
            favorite = Favorite.objects.filter(
                user=request.user, recipe=recipe
            )
            if favorite.exists():
                favorite.delete()
                return Response(
                    {'detail': 'Рецепт удален из избранного.'},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {'detail': 'Рецепт не найден в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
