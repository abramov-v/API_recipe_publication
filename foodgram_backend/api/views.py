from djoser.views import UserViewSet

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)

from api.paginators import CustomPagination
from api.serializers import (TagSerializer, IngredientSerializer, RecipeListSerializer)
from recipes.models import Recipe, Tag, Ingredient
from django_filters.rest_framework import DjangoFilterBackend
from api.permissions import AdminOrReadOnly
from users.models import Subscription
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
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('post', 'patch', 'delete'):
            pass
        return RecipeListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
