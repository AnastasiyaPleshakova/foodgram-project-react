from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

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
    min_num = 1


class TagRecipeTabular(admin.TabularInline):
    model = TagRecipe
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'name',
        'author', 'get_image',
        'pub_date', 'get_ingredients',
        'get_tags', 'get_count_favorites',
    )
    list_filter = ('name', 'author', 'tags',)
    list_editable = ('name', 'author',)
    search_fields = ('name',)
    inlines = [IngredientRecipeTabular, TagRecipeTabular, ]

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join([
            ingredient.name for ingredient in obj.ingredients.all()
        ])

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ', '.join([
            tag.name for tag in obj.tags.all()
        ])

    @admin.display(description='Кол-во в избранном')
    def get_count_favorites(self, obj):
        return obj.favorites.count()

    @admin.display(description='Изображение')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')


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
