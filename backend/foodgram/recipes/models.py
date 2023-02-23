from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from users.models import User


# объявляем класс Ingredient - наследник класса Model
# в соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта
class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        'Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.name


# объявляем класс Tag - наследник класса Model
# в соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта
# все поля в модели Тег обязательны и уникальны
class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(
        'Название',
        unique=True,
        max_length=200
    )
    # для поля color нужно применить валидатор, чтобы проверить,
    # что введено корректное значение - цветовой код в нужном формате
    # если в представленном пользователем значении не будет
    # соответствующего - т.е в нужном формает, то вернется message
    # с ошибкой
    color = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=(
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Введенное значение не является цветовым HEX-кодом!'))
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег',
        verbose_name_plural = 'Теги',

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.name


# объявляем класс Recipe - наследник класса Model
# в соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта
class Recipe(models.Model):
    """Модель рецепта."""
    # поле author поле отношения с моделью User
    # указываем модель, связь с которой обеспечивает это поле - User
    # указываем опцию on_delete со значением SET_NULL, то есть при удалении
    # пользователя, во всех рецептах этого автора
    # будет указан None или анонимный автор
    # обязательно нужно указать null=True - то есть, допускается значение  NULL
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.SET_NULL,
        null=True
    )

    # поле представляет собой связь с таблицей Tags
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes'
    )

    # поле представляет собой связь с таблицей Ingredients
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингридиенты',
        related_name='recipes'
    )

    # текстовое поле с названием рецепта
    # имеет ограничение по длине текста
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )

    # поле для изображения с рецептом
    # укажем опцию upload_to -
    # здесь указываем папку для сохранения файлов этого поля
    # этот путь относительный и он продолжает путь указанный в MEDIA_ROOT
    # то есть, путь будет '/media_root/recipes/'
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/'
    )
    # текстовое поле с описанием рецепта
    # не имеет ограничения по длине текста
    text = models.TextField(
        'Описание рецепта'
    )

    # поле время приготовления должно быть положительным числовым значением
    # для того чтобы проверить поле на соответствие минимальному значению
    # используем встроенный валидатор
    cooking_time = models.IntegerField(
        'Время приготовления (мин)',
        validators=(MinValueValidator(
            1,
            message='Минимально допустимое значение - 1 минута!'),)
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.name
