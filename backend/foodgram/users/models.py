from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings


# Create your models here.
# Создаем кастомную модель пользователя - наследник от AbstractUser
# в дальнейшем использование этого класса упростит внесение изменений
# в модель пользователя, расширение функциональности пользователя
class User(AbstractUser):
    """Модель пользователя."""
    # создаем поля, сверяя с исходным кодом класса AbstractUser
    # проверяя соответствие требованиям ТЗ(redoc)

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        # default='default_email'

    )
    username = models.CharField(
        verbose_name='Уникальный юзернэйм',
        max_length=settings.MAX_LEN_FIELD_USER,
        unique=True,
        # default='default_username',

        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимое имя пользователя'
            ),
        )
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.MAX_LEN_FIELD_USER
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.MAX_LEN_FIELD_USER
    )

    # password = models.CharField(
    #     verbose_name='Пароль пользователя',
    #     max_length=settings.MAX_LEN_FIELD_USER,
    #     # default='default_password'
    # )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.username


# создаем модель подписки
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
        # в классе Meta необходимо задать опцию constraints
        # применяем класс UniqueConstraints
        # чтобы указать уникальность подписки - т.е
        # нельзя дважды подписаться на одного автора рецепта
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscribe'
            ),
        )

    def __str__(self):
        return (f'{self.user} подписан на {self.author}')
