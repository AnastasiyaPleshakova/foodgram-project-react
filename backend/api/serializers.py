import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework.serializers import (
    CurrentUserDefault, ImageField, IntegerField,
    ListField, ModelSerializer, PrimaryKeyRelatedField,
    ReadOnlyField, SerializerMethodField, ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from api.validators import MyValidationError
from recipes.models import Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe
from users.models import User


class UserBaseSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        abstract = True
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and not request.user.is_anonymous
                and obj.subscription.filter(user=request.user).exists()
                )


class CustomUserSerializer(UserBaseSerializer):
    pass


class Base64ImageField(ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            media_type, image_string = data.split(';base64,')
            image_format = media_type.split('/')[-1]
            data = ContentFile(
                base64.b64decode(image_string),
                name='temp.' + image_format
            )
        return super().to_internal_value(data)


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_field = '__all__'


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_field = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit'),
                message='Ингредиент уже существует',
            )
        ]


class IngredientRecipeListSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')
    amount = ReadOnlyField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = SerializerMethodField()
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags',
            'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image',
            'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (
                request
                and not request.user.is_anonymous
                and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
                request
                and not request.user.is_anonymous
                and obj.shopping_cart.filter(user=request.user).exists()
        )

    def get_ingredients(self, obj):
        return IngredientRecipeListSerializer(
            IngredientRecipe.objects.filter(recipe=obj),
            many=True
        ).data


class IngredientRecipeSerializer(ModelSerializer):
    # id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount',)

    # валидация для вывода статуса ответа - 404
    def validate(self, data):
        id_ingredient = data.get('id')
        if Ingredient.objects.filter(id=id_ingredient).exists():
            return data
        raise MyValidationError({
            'detail': f'Ингредиент c id "{id_ingredient}" не существует'
        })


class RecipeSerializer(ModelSerializer):
    author = PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUserDefault()
    )
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    tags = ListField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'tags',
            'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = ('author', )

    validators = [
        UniqueTogetherValidator(
            queryset=Recipe.objects.all(),
            fields=('name', 'author'),
            message='Данный рецепт опубликован вами ранее',
        )
    ]

    def validate(self, data):
        ingredients = data.get('ingredients')
        unique_ingredients = []
        id_tags = data.get('tags')
        for ingredient in ingredients:
            if ingredient.get('amount') == 0:
                raise ValidationError({
                    'amount': 'Минимальное количество ингредиентов - 1 ед.'
                })
            if ingredient in unique_ingredients:
                raise ValidationError({
                    'ingredients': 'Выбраны повторяющиеся ингредиенты.'
                })
            unique_ingredients.append(ingredient)
        # срабатывает валидатор на уровне модели
        # if data.get('cooking_time') == 0:
        #     raise ValidationError({
        #         'cooking_time': 'Минимальное время приготовления - 1 минута.'
        #     })
        if len(ingredients) == 0:
            raise ValidationError({
                'ingredients':
                'Добавьте хотя бы одно наименование ингредиента.'
            })
        if len(id_tags) == 0:
            raise ValidationError({
                'tags': 'Добавьте хотя бы один тег.'
            })
        # валидация для вывода статуса ответа - 404
        for id_tag in id_tags:
            if not Tag.objects.filter(id=id_tag).exists():
                raise MyValidationError({
                    'detail': f'Тег c id "{id_tag}" не существует'
                })
            if len(set(id_tags)) < len(id_tags):
                raise ValidationError({
                    'tags': 'Выбраны повторяющиеся теги.'
                })
        return data

    def create_link_ingredients_tags(self, ingredients, id_tags, recipe):
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=ingredient.get('id')),
                amount=ingredient.get('amount'),
            )
        for id_tag in id_tags:
            TagRecipe.objects.create(
                recipe=recipe,
                tag=Tag.objects.get(id=id_tag),
            )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        id_tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.create_link_ingredients_tags(ingredients, id_tags, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        id_tags = validated_data.pop('tags')
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        self.create_link_ingredients_tags(ingredients, id_tags, instance)
        instance.save()
        return instance


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_field = '__all__'


class SubscriptionListSerializer(UserBaseSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(UserBaseSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        print(obj)
        limit = self.context.get('request').query_params.get('recipes_limit')
        if limit:
            return ShortRecipeSerializer(Recipe.objects.filter(
                author=obj)[:int(limit)],
                many=True
            ).data
        return ShortRecipeSerializer(
            Recipe.objects.filter(author=obj),
            many=True
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
