from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings


class User(AbstractUser):
    """Модель пользователя."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернэйм',
        max_length=settings.MAX_LEN_FIELD_USER,
        unique=True,
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимое имя пользователя'
            ),
        )
    )
    first_name = models.CharField(
        'Имя',
        blank=True,
        max_length=settings.MAX_LEN_FIELD_USER
    )
    last_name = models.CharField(
        'Фамилия',
        blank=True,
        max_length=settings.MAX_LEN_FIELD_USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.username


class Subscription(models.Model):
    """Модель подписки."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='subscribing'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            ),
        )

    def __str__(self):
        return (f'{self.user} подписан на {self.author}')
