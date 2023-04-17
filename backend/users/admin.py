from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    @admin.display(description='Кол-во рецептов')
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description='Кол-во подписчиков')
    def subscribers_count(self, obj):
        return obj.subscription.count()

    list_display = (
        'pk', 'username',
        'password', 'email',
        'recipes_count', 'subscribers_count',
    )
    list_display_links = ('pk', 'username',)
    list_filter = ('username', 'email',)
    search_fields = ('name',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author',)
