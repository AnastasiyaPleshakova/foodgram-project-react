from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    APISubscription,
    APISubscriptionList,
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('users/subscriptions/', APISubscriptionList.as_view()),
    path('users/<int:author_id>/subscribe/', APISubscription.as_view()),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
