from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    CurrentUserDefault, IntegerField,
    ListField, ModelSerializer,
    PrimaryKeyRelatedField, ReadOnlyField,
    SerializerMethodField, ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from api.validators import ChangeResponseStatusValidationError
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag
)
from users.models import Subscription, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id',
            'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and obj.subscription.filter(user=request.user).exists()
                )


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
                and request.user.is_authenticated
                and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (
                request
                and request.user.is_authenticated
                and obj.shopping_cart.filter(user=request.user).exists()
        )

    def get_ingredients(self, obj):
        return IngredientRecipeListSerializer(
            IngredientRecipe.objects.filter(recipe=obj), many=True).data


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
        if not Ingredient.objects.filter(id=id_ingredient).exists():
            raise ChangeResponseStatusValidationError({
                'detail': f'Ингредиент c id "{id_ingredient}" не существует'
            })
        return data


class RecipeSerializer(ModelSerializer):
    author = PrimaryKeyRelatedField(
        read_only=True,
        default=CurrentUserDefault()
    )
    image = Base64ImageField()
    ingredients = IngredientRecipeSerializer(many=True)
    tags = ListField()
    cooking_time = IntegerField()
    # tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

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
            if ingredient.get('amount') <= 0:
                raise ValidationError({
                    'amount': 'Минимальное количество ингредиентов - 1 ед.'
                })
            if ingredient in unique_ingredients:
                raise ValidationError({
                    'ingredients': 'Выбраны повторяющиеся ингредиенты.'
                })
            unique_ingredients.append(ingredient)
        if data.get('cooking_time') <= 0:
            raise ValidationError({
                'cooking_time': 'Минимальное время приготовления - 1 минута.'
            })
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
                raise ChangeResponseStatusValidationError({
                    'detail': f'Тег c id "{id_tag}" не существует'
                })
            if len(set(id_tags)) < len(id_tags):
                raise ValidationError({
                    'tags': 'Выбраны повторяющиеся теги.'
                })
        return data

    def create_link_ingredients(self, ingredients, recipe):
        ingredient_list = [
            IngredientRecipe(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        ]
        ingredient_list.sort(
            key=lambda element: element.ingredient.name,
            reverse=True
        )
        IngredientRecipe.objects.bulk_create(objs=ingredient_list)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        id_tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            **validated_data,
            author=self.context.get('request').user,
        )
        recipe.tags.set(id_tags)
        self.create_link_ingredients(ingredients, recipe)
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(instance, context=self.context).data

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        id_tags = validated_data.pop('tags')
        IngredientRecipe.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        instance.tags.set(id_tags)
        self.create_link_ingredients(ingredients, instance)
        instance.save()
        return super().update(instance, validated_data)


class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)
        read_only_field = '__all__'


class SubscriptionListSerializer(CustomUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_field = '__all__'

    def validate(self, data):
        if self.Meta.model.objects.filter(
                user=self.context.get('request').user,
                recipe=data.get('recipe'),
        ).exists():
            raise ValidationError({'error': 'Рецепт уже добавлен.'})
        return data

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartSerializer(FavoriteSerializer):

    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart


class SubscriptionSerializer(ModelSerializer):

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_field = '__all__'

    def validate(self, data):
        author = data.get('author')
        user = self.context.get('request').user
        if author == user:
            raise ValidationError({
                'error': 'Вы пытаетесь подписаться на себя.'
            })
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError({
                'error': 'Подписка на пользователя уже существует.'
            })

        return data

    def to_representation(self, instance):
        return SubscriptionListSerializer(
            instance.author, context=self.context
        ).data
