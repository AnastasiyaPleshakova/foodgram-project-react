import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginations import LimitCustomPagination
from api.permissons import IsAuthorOrAdminOrReadOnly
from api.serializers import (
    IngredientSerializer, RecipeListSerializer, RecipeSerializer,
    ShortRecipeSerializer, SubscriptionListSerializer, TagSerializer,
)
from recipes.models import (
    Favorite, Ingredient,
    IngredientRecipe, Recipe,
    ShoppingCart, Tag,
)
from users.models import Subscription, User


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly,)
    pagination_class = LimitCustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def action_recipe_favorite_shoppingcart(model, request, pk, message):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if model.objects.filter(user=user, recipe=recipe).exists():
            if request.method == 'POST':
                return Response({
                    'error': 'Рецепт уже добавлен.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.method == 'POST':
            model.objects.create(
                user=user,
                recipe=recipe,
            )
            return Response(
                ShortRecipeSerializer(recipe).data,
                status=status.HTTP_201_CREATED,
            )
        return Response({
            'error': f'Рецепт отсутствует в {message}.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        return self.action_recipe_favorite_shoppingcart(
            Favorite, request, pk, 'избранном'
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        return self.action_recipe_favorite_shoppingcart(
            ShoppingCart, request, pk, 'списке покупок'
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        INDENT = 20
        HEADER_HEIGHT = 800
        height_text = 770
        number = 1
        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')).order_by('ingredient')
        pdfmetrics.registerFont(TTFont('TNR', 'times.ttf'))
        pdfmetrics.registerFont(TTFont('TNRB', 'timesbd.ttf'))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont('TNRB', 20)
        p.drawString(INDENT, HEADER_HEIGHT, 'Список ингредиентов:')
        p.setFont('TNR', 15)
        for ingredient in ingredients:
            print(ingredient)
            p.drawString(
                INDENT,
                height_text,
                f'{number}. '
                f'{ingredient["ingredient__name"]}'
                f' - {ingredient["amount__sum"]}'
                f'{ingredient["ingredient__measurement_unit"]}')
            height_text -= 20
            number += 1
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )


class APISubscriptionList(ListAPIView):
    serializer_class = SubscriptionListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitCustomPagination

    def get_queryset(self):
        return User.objects.filter(subscription__user=self.request.user)


class APISubscription(APIView):

    def post(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('author_id'))
        if user == author:
            return Response(
                {'error': 'Вы пытаетесь подписаться на самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'error': f'Подписка на пользователя "{author.first_name} '
                          f'{author.last_name}" уже существует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.create(user=user, author=author)
        return Response(
            SubscriptionListSerializer(
                author,
                context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, **kwargs):
        user = request.user
        author = get_object_or_404(User, id=self.kwargs.get('author_id'))
        if user == author:
            return Response(
                {'error': 'Вы пытаетесь отписаться от самого себя.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not Subscription.objects.filter(user=user, author=author).exists():
            return Response(
                {'error': f'Подписка на пользователя "{author.first_name} '
                          f'{author.last_name}" не существует.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.filter(user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
