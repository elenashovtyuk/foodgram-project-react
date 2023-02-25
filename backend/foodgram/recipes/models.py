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
                message='Введенное значение не является цветовым HEX-кодом!'),)
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

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


# объявляем класс RecipeIngredient -
# наследник класса Model
# это промежуточная модель между Recipe и Ingredient
# ее нужно задавать "вручную", так как необходимы дополнительные поля
# в промежуточной модели помимо тех, что автоматически создаются
class RecipeIngredient(models.Model):
    """Модель ингредиентов в составе рецепта"""
    # сначала явно указываем поля - внешние ключи от моделей,
    #  которые учавствуют в этой связи ManyToMany
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipes'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredients'
    )
    # далее в этой промежуточной модели должно быть дополнительное
    # поле по кол-ву ингредиентов
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1, message='Минимальное количество 1!')])

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
    """Модель избранных рецептов."""
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
