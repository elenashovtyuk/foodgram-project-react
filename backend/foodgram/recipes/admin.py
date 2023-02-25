from django.contrib import admin

# Регистрируем модель Recipe
# сначала импортируем ее из нашего модуля models.py
from .models import Ingredient, Recipe, RecipeIngredient, Tag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
# для настройки отображения модели Recipe в админке применяем класс
# AdminModel, который связывается с моделью Recipe и конфигурирует
# отображение данных этой модели в интерфейсе админки


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    # перечисляем поля, которые должны отображаться в админке
    # по ТЗ для модели рецептов в админ-зону в списке рецептов
    # нужно вывести название рецепта и автора рецепта
    list_display = ('pk', 'name', 'author', 'count_favorite_recipe')
    # также по ТЗ нужно вывести фильтры по автору, названию рецепта и тегам
    list_filter = ('author', 'name', 'tags')

    # также по ТЗ нужно вывести общее кол-во добавлений этого рецепта
    # в избранное. Для этого необходимо написать функцию действия
    # которая будет возвращать общее кол-во добавления рецепта в избранное
    def count_favorite_recipe(self, obj):
        return obj.favorite_recipe.count()
    count_favorite_recipe.short_description = 'В избранном'


# для настройки отображения модели Ingredient в админке применяем класс
# AdminModel, который связывается с моделью Ingredient и конфигурирует
# отображение данных этой модели в интерфейсе админки
class IngredientAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline,)
    # далее согласно ТЗ перечисляем поля, которые должны отображаться в админке
    # это название и ед.измерения
    list_display = ('pk', 'name', 'measurement_unit')
    # также по ТЗ нужно настроить фильтрацию по названию
    list_filter = ('name',)


# для настройки отображения модели Tag в админке применяем класс
# AdminModel, который связывается с моделью Tag и конфигурирует
# отображение данных этой модели в интерфейсе админки
class TagAdmin(admin.ModelAdmin):
    # далее перечисляем поля, которые должны отображаться в админке - все
    list_display = ('pk', 'name', 'color', 'slug')


# при регистрации модели Recipe источником конфигурации для нее
# назначаем RecipeAdmin
admin.site.register(Recipe, RecipeAdmin)
# при регистрации модели Ingredient в админ-зоне
# источником конфигурации для нее назначенм IngredientAdmin
admin.site.register(Ingredient, IngredientAdmin)
# при регистрации модели Tag в админ-зоне
# источником конфигурации для нее назначенм TagAdmin
admin.site.register(Tag, TagAdmin)
# admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
