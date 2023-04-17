from django.conf import settings
from django.core.validators import MinValueValidator, validate_slug
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Наименование',
        unique=True,
        max_length=settings.CHAR_MAX_LENGTH,
    )
    color = models.CharField(
        'Цветовой HEK-код',
        unique=True,
        max_length=settings.COLOR_MAX_LENGTH,
    )
    slug = models.CharField(
        unique=True,
        max_length=settings.CHAR_MAX_LENGTH,
        validators=(validate_slug,)
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name[:settings.STR_MAX_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        'Наименование',
        max_length=settings.CHAR_MAX_LENGTH,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.CHAR_MAX_LENGTH,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name', 'measurement_unit')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            ),
        ]

    def __str__(self):
        return (
            f'{self.name[:settings.STR_MAX_LENGTH]} ({self.measurement_unit})'
        )


class Recipe(models.Model):
    name = models.CharField(
        'Наименование',
        max_length=settings.CHAR_MAX_LENGTH,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='recipes',
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True,
    )
    text = models.TextField('Описание', )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин',
        validators=[MinValueValidator(
            1, 'Минимальное время приготовления - 1 минута.'
        )]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'author'],
                name='unique_author_recipe',
            ),
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(
            1, 'Минимальное количество ингредиентов - 1 ед.'
        )]
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f'{self.ingredient.name[:settings.STR_MAX_LENGTH]} - {self.amount}'
            f'{self.ingredient.measurement_unit}'
        )


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f'{self.recipe.name[:settings.STR_MAX_LENGTH]}'
            f' - {self.tag.name}'
        )


class FavoriteShoppingCartBaseModel(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('recipe',)

    def __str__(self):
        return self.recipe.name[:settings.STR_MAX_LENGTH]


class Favorite(FavoriteShoppingCartBaseModel):
    class Meta(FavoriteShoppingCartBaseModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorite_recipe',
            ),
        ]


class ShoppingCart(FavoriteShoppingCartBaseModel):

    class Meta(FavoriteShoppingCartBaseModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shopping_cart_recipe',
            ),
        ]
