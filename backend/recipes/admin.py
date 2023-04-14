from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe,
    Recipe, ShoppingCart, Tag, TagRecipe,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_filter = ('name',)
    list_editable = ('name', 'color', 'slug',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit',)
    list_filter = ('name',)
    list_editable = ('name', 'measurement_unit',)
    search_fields = ('name',)


class IngredientRecipeTabular(admin.TabularInline):
    model = IngredientRecipe


class TagRecipeTabular(admin.TabularInline):
    model = TagRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name',
        'author', 'image',
        'pub_date', 'get_ingredients',
        'get_tags', 'get_count_favorites',
    )
    list_filter = ('name', 'author', 'tags',)
    list_editable = ('name', 'author',)
    search_fields = ('name',)
    inlines = [IngredientRecipeTabular, TagRecipeTabular, ]

    def get_ingredients(self, obj):
        return ', '.join([
            str(ingredient) for ingredient in obj.ingredients.all()
        ])

    def get_tags(self, obj):
        return ', '.join([
            str(tag) for tag in obj.tags.all()
        ])

    def get_count_favorites(self, obj):
        return obj.favorites.count()

    get_ingredients.short_description = 'Ингредиенты'
    get_tags.short_description = 'Теги'
    get_count_favorites.short_description = 'Количество добавлений в избранное'


@admin.register(IngredientRecipe)
class IngredientRecipe(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient',)
    search_fields = ('reipe',)


@admin.register(TagRecipe)
class TagRecipe(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'tag',)
    list_filter = ('recipe',)
    search_fields = ('reсipe',)


@admin.register(Favorite)
class FavoriteRecipe(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user',)
    list_filter = ('recipe',)
    search_fields = ('reсipe',)


@admin.register(ShoppingCart)
class ShoppingCart(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user',)
    list_filter = ('recipe',)
    search_fields = ('reсipe',)


admin.site.unregister(Group)
