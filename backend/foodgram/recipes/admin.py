from django.contrib import admin

# Регистрируем модель Recipe
# сначала импортируем ее из нашего модуля models.py
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
# для настройки отображения модели Recipe в админке применяем класс
# ModelAdmin, который связывается с моделью Recipe и конфигурирует
# отображение данных этой модели в интерфейсе админки


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Управление рецептами."""
    inlines = (RecipeIngredientInline,)
    # перечисляем поля, которые должны отображаться в админке
    # по ТЗ для модели рецептов в админ-зону в списке рецептов
    # нужно вывести название рецепта и автора рецепта
    list_display = ('pk', 'name', 'author', 'count_favorite_recipe')
    # также по ТЗ нужно вывести фильтры по автору, названию рецепта и тегам
    list_filter = ('author', 'name', 'tags')
    list_editable = ('author',)

    # также по ТЗ нужно вывести общее кол-во добавлений этого рецепта
    # в избранное. Для этого необходимо написать функцию действия
    # которая будет возвращать общее кол-во добавления рецепта в избранное
    def count_favorite_recipe(self, obj):
        return obj.favorite_recipe.count()
    count_favorite_recipe.short_description = 'В избранном'


# для настройки отображения модели Ingredient в админке применяем класс
# ModelAdmin, который связывается с моделью Ingredient и конфигурирует
# отображение данных этой модели в интерфейсе админки
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Управление ингредиентами."""
    # inlines = (RecipeIngredientInline,)
    # далее согласно ТЗ перечисляем поля, которые должны отображаться в админке
    # это название и ед.измерения
    list_display = ('pk', 'name', 'measurement_unit')
    # также по ТЗ нужно настроить фильтрацию по названию
    list_filter = ('name',)
    search_fields = ('name',)


# для настройки отображения модели Tag в админке применяем класс
# ModelAdmin, который связывается с моделью Tag и конфигурирует
# отображение данных этой модели в интерфейсе админки
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Управление тегами."""
    # далее перечисляем поля, которые должны отображаться в админке - все
    list_display = ('pk', 'name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')


# для настройки отображения модели Favorite в админке применяем класс
# ModelAdmin, который связывается с моделью Favorite и конфигурирует
# отображение данных этой модели в интерфейсе админки
@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Управление избранными рецептами."""
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Управление рецептами в списке покупок."""
    list_display = ('user', 'recipe')
    search_fields = ('user', 'recipe')
