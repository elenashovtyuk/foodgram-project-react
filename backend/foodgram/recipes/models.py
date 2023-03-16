from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User
from django.conf import settings


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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_measurement_unit_for_ingredient'
            ),
        )

    def __str__(self):
        """Cтроковое представление объекта модели"""
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель описания тегов для рецептов."""
    name = models.CharField(
        'Название тега',
        unique=True,
        max_length=settings.MAX_LEN_FIELD,
    )
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


class Recipe(models.Model):
    """Модель описания рецепта."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        related_name='recipes',
        on_delete=models.CASCADE
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='recipes',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингридиенты',
        related_name='recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LEN_FIELD,
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/',
    )
    text = models.TextField(
        'Описание рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (мин)',
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                message='Минимально допустимое значение - 1 минута!'
            ),
        )
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)
        constraints = (
            models.UniqueConstraint(
                fields=('name',),
                name='unique_recipe'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели."""
        return f'{self.name} (Автор: {self.author.username})'


class RecipeIngredient(models.Model):
    """
    Модель для связи Recipe и Ingredient.
    Содеражит сведения о количестве ингредиентов.
    """

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Связанный рецепт',
        related_name='recipe_to_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Связанные ингредиенты',
        related_name='ingredient_to_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                settings.MIN_AMOUNT_INGR,
                message='Минимальное количество 1!'),
        )
    )

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
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount}'
            f'{self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """
    Модель избранных рецептов.
    Связь моделей Recipe и User.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь, добавивший в избранное',
        related_name='favorite_recipe'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт, добавленный в избранное',
        related_name='favorite_recipe'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite_recipe'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.user.username + 'добавил в Избранное' + self.recipe.name


class ShoppingCart(models.Model):
    """
    Модель списка покупок.
    Связь моделей User и Recipe.
    """
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='carts',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт добавленный в список покупок',
        related_name='carts',
        on_delete=models.CASCADE
    )
    add_date = models.DateTimeField(
        'Дата добавления рецепта в список покупок',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт в списке покупок'
        verbose_name_plural = 'Рецепты в списке покупок'
        ordering = ('-add_date',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipe_in_cart'
            ),
        )

    def __str__(self):
        """Строковое представление объекта модели."""
        return self.recipe.name + 'в списке покупок' + self.user.username
