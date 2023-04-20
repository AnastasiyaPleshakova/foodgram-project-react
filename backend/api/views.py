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
    IngredientSerializer, FavoriteSerializer,
    RecipeListSerializer, RecipeSerializer,
    ShoppingCartSerializer, SubscriptionListSerializer,
    SubscriptionSerializer, TagSerializer,
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

    @staticmethod
    def post_method_for_favorite_shoppingcart(serializer, request, pk):
        serializer = serializer(
            data={'recipe': pk, 'user': request.user.pk},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_favorite_shoppingcart(model, request, pk):
        get_object_or_404(
            model, user=request.user, recipe=get_object_or_404(Recipe, pk=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post'], detail=True)
    def favorite(self, request, pk):
        return self.post_method_for_favorite_shoppingcart(
            FavoriteSerializer, request, pk,
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_favorite_shoppingcart(
            Favorite, request, pk,
        )

    @action(methods=['post'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_method_for_favorite_shoppingcart(
            ShoppingCartSerializer, request, pk,
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_favorite_shoppingcart(
            ShoppingCart, request, pk,
        )

    @staticmethod
    def create_pdf_file(ingredients):
        INDENT = 20
        HEADER_HEIGHT = 800
        height_text = 770
        number = 1
        pdfmetrics.registerFont(TTFont('FreeSans', 'data/FreeSans.ttf'))
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont('FreeSans', 23)
        p.drawString(INDENT, HEADER_HEIGHT, 'Список ингредиентов:')
        p.setFont('FreeSans', 15)
        for ingredient in ingredients:
            p.drawString(
                INDENT,
                height_text,
                f'{number}. '
                f'{ingredient["ingredient__name"]}'
                f' - {ingredient["amount__sum"]}'
                f'{ingredient["ingredient__measurement_unit"]}'
            )
            height_text -= 20
            number += 1
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='shopping_cart.pdf'
        )

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):

        ingredients = IngredientRecipe.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(Sum('amount')).order_by('ingredient')
        return self.create_pdf_file(ingredients)


class APISubscriptionList(ListAPIView):
    serializer_class = SubscriptionListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = LimitCustomPagination

    def get_queryset(self):
        return User.objects.filter(subscription__user=self.request.user)


class APISubscription(APIView):

    def post(self, request, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('author_id'))
        serializer = SubscriptionSerializer(
            data={'author': author.pk, 'user': request.user.pk},
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, **kwargs):
        get_object_or_404(
            Subscription,
            author=get_object_or_404(User, id=self.kwargs.get('author_id')).pk,
            user=request.user.pk,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
