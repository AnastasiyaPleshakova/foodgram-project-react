from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


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
        ordering = ('author',)
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

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
