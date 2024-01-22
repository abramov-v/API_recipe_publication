from djoser.views import UserViewSet
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db import IntegrityError
from django.db.models import Sum
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.paginators import CustomPagination
from api.serializers import (TagSerializer, IngredientSerializer, RecipeListSerializer, RecipeCreateSerializer, SubscriptionsSerializer, RecipeForSubscriptionSerializer)
from recipes.models import Recipe, Tag, Ingredient
from django_filters.rest_framework import DjangoFilterBackend
from api.permissions import IsAuthorOrReadOnly
from users.models import Subscription
from recipes.models import ShoppingCart, RecipeIngredient
from rest_framework import status, viewsets
from rest_framework.response import Response
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from api.filters import IngredientSearchFilter, RecipeFilter    



User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Api для работы с пользователями."""
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
        serializer = SubscriptionsSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        if request.user.id == author.id:
            return Response({'detail': 'Нельзя подписаться на самого себя'}, status=status.HTTP_400_BAD_REQUEST) 
               
        try:
            Subscription.objects.create(user=request.user, author=author)
        except IntegrityError:
            return Response({'detail': 'Вы уже подписаны на этого пользователя'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionsSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def unsubscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        subscription = Subscription.objects.filter(user=request.user, author=author)
        if subscription.exists():
            subscription.delete()
            return Response({'detail': 'Unsubscribed successfully.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'You are not subscribed to this user.'}, status=status.HTTP_400_BAD_REQUEST)

  
class TagViewSet(ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipesViewSet(ModelViewSet):
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
    
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).exists:
                return Response({'detail': 'Уже в корзине'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = RecipeForSubscriptionSerializer(recipe)
            return Response(data=serializer.data,
                            status=status.HTTP_201_CREATED)
        deleted = get_object_or_404(ShoppingCart,
                                    user=request.user,
                                    recipe=recipe)
        deleted.delete()
        return Response({'message': 'Рецепт успешно удален из списка покупок'},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user).values(
                'ingredients__name',
                'ingredients__measurement_unit').annotate(
                    amount=Sum('amount'))
        data = ingredients.values_list('ingredients__name',
                                       'ingredients__measurement_unit',
                                       'amount')
        shopping_cart = 'Список покупок:\n'
        for name, measure, amount in data:
            shopping_cart += (f'{name.capitalize()} {amount} {measure},\n')
        response = HttpResponse(shopping_cart, content_type='text/plain')
        return response
