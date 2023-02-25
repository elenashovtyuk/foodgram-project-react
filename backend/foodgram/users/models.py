from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


# Create your models here.
# Создаем кастомную модель пользователя - наследник от AbstractUser
# в дальнейшем использование этого класса упростит внесение изменений
# в модель пользователя, расширение функциональности пользователя
class User(AbstractUser):
    # создаем поля, сверяя с исходным кодом класса AbstractUser
    # проверяя соответствие требованиям ТЗ(redoc)
    # поля first_name и last_name не указываем явно - так как они
    # полностью соответствуют полям родительской модели - AbstractUser
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        default='default_email'

    )
    username = models.CharField(
        verbose_name='Уникальный юзернэйм',
        max_length=150,
        unique=True,
        default='default_username',
        validators=(
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Недопустимое имя пользователя'
            ),
        )
    )

    password = models.CharField(
        verbose_name='Пароль пользователя',
        max_length=150,
        default='default_password'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.username
