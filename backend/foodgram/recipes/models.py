from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User
from django.conf import settings

# Модели приложения recipes:

# В соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта


# объявляем класс Ingredient - наследник класса Model
class Ingredient(models.Model):
    """Модель описания ингредиентов для рецепта."""
    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_LEN_FIELD,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_LEN_FIELD,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        """Cтроковое представление объекта модели"""
        return f'{self.name} ({self.measurement_unit})'


# объявляем класс Tag - наследник класса Model
# все поля в модели Тег обязательны и уникальны
class Tag(models.Model):
    """Модель описания тегов для рецептов."""
    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=settings.MAX_LEN_FIELD,
    )
    # для поля color используем ColorField
    # предварительно установив пакет django-colorfield
    # и добавив модуль в settings.py/INSTALLED_APPS
    color = ColorField(
        'Цветовой HEX-код',
        format='hex',
        unique=True,
        max_length=settings.MAX_LEN_HEX_FIELD,
    )
    slug = models.SlugField(
        'Уникальный слаг тега',
        unique=True,
        max_length=settings.MAX_LEN_FIELD,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        """Строковое представление объекта модели."""
        return f'{self.name} (цвет: {self.color})'


# объявляем класс Recipe - наследник класса Model
# в соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта
class Recipe(models.Model):
    """Модель описания рецепта."""
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
        null=True,
    )

    # поле представляет собой связь с таблицей Tags
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )

    # поле представляет собой связь с таблицей Ingredients
    # связь ManyToMany
    # промежуточная модель в Django создается автоматически,
    # но если нужно в промежуточной модели указать дополнительные поля
    # то есть, не только recipe_id и ingredient_id, то нужно
    # то нужно эту промежуточную модель задать вручную,
    # а для ingredient в модели recipe указать через опцию througth
    # через какую модель это поле ingredient связано с моделью Recipe
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты',
        related_name='recipes',
    )

    # текстовое поле с названием рецепта
    # имеет ограничение по длине текста
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LEN_FIELD,
    )

    # поле для изображения с рецептом
    # укажем опцию upload_to -
    # здесь указываем папку для сохранения файлов этого поля
    # этот путь относительный и он продолжает путь указанный в MEDIA_ROOT
    # то есть, путь будет '/media_root/recipes/'
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/',
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
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message='Минимально допустимое значение - 1 минута!',
            ),
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        """Строковое представление объекта модели."""
        return f'{self.name} (Автор: {self.author.username})'


# объявляем класс RecipeIngredient -
# наследник класса Model
# это промежуточная модель между Recipe и Ingredient
# ее нужно задавать "вручную", так как необходимы дополнительные поля
# в промежуточной модели помимо тех, что автоматически создаются
class RecipeIngredient(models.Model):
    """
    Модель для связи Recipe и Ingredient.
    Содеражит сведения о количестве ингредиентов.
    """
    # сначала явно указываем поля - внешние ключи от моделей,
    #  которые учавствуют в этой связи ManyToMany
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Связанный рецепт',
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Связанные ингредиенты',
        related_name='recipes'
    )
    # далее в этой промежуточной модели должно быть дополнительное
    # поле по кол-ву ингредиентов
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGR,
                message='Минимальное количество 1!')
        )
    )

    # в настройках модели, в классе Meta нужно указать уникальность комбинации
    # ингредиент-рецепт
    # рецепт-ингредиент с помощью опции constraints
    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели."""
        return (
            f'{self.recipe.name}: ',
            f'{self.ingredient.name} - ',
            f'{self.amount}',
            f'{self.ingredient.measurement_unit}'
        )


# объявляем класс Favorite(Избранное)
# это модель рецептов, добавленных в избранное пользователем
# в соответствии с Django Coding Style поочередно выполняем след.шаги:
# первый шаг - описываем поля модели, их типы, свойства
# второй шаг - описываем класс Meta, чтобы добавить данные о самой модели
# третий шаг - указываем метод __str__ - строковое представление объекта
class Favorite(models.Model):
    """
    Модель связи Recipe и  User.
    Содержит сведения об избранных рецептах пользователя.
    """
    # 1-ое поле - пользователь, который добавил рецепт в Избраннное
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, добавивший в избранное',
        related_name='favorite_recipe'
    )
    # 2-ое поле - рецепт, который добавили в избранное
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, добавленный в избранное',
        related_name='favorite_recipe'
    )

    # далее класс Meta
    # в поведении этой модели необходимо указать,
    # что пользователь может только однажды добавить рецепт в избранное
    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    # далее магический метод str
    def __str__(self):
        """Строковое представление объекта модели."""
        return f'Пользователь {self.user} добавил "{self.recipe}" в Избранное'
