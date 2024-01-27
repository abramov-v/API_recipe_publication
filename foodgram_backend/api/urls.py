from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.views import (
    RecipesViewSet,
    CustomUserViewSet,
    TagViewSet,
    IngredientViewSet
)

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'recipes', RecipesViewSet)
router_v1.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    url(r'^auth/', include('djoser.urls.authtoken')),
    url(r'', include(router_v1.urls)),
]
