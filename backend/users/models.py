import re

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers


def validate_username(value):
    USERNAME_ME = 'Нельзя использовать "me" в качестве username'
    USERNAME_EMPTY = 'Поле "username" не должно быть пустым'
    if value == 'me' or '':
        invalid_username = USERNAME_ME if (
            value == 'me') else USERNAME_EMPTY
        raise serializers.ValidationError(detail=[invalid_username])
    result = re.findall(r'[^\w.@+-]', value)
    if result:
        raise serializers.ValidationError(
            f'Некорректные символы в username:'
            f' `{"`, `".join(set(result))}`.'
        )
    return value


class User(AbstractUser):
    email = models.EmailField(
        'Электронная почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
    )
    username = models.CharField(
        'Логин',
        max_length=settings.USER_MAX_LENGTH,
        validators=[validate_username],
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.USER_MAX_LENGTH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.USER_MAX_LENGTH,
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        related_name='subscriber',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='subscription',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            )
        ]
