from django.contrib import admin

# Регистрируем модель Recipe
# сначала импортируем ее из нашего модуля models.py
from .models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag


# для настройки отображения модели Recipe в админке применяем класс
# AdminModel, который связывается с моделью Recipe и конфигурирует
# отображение данных этой модели в интерфейсе админки
class RecipeAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    # по ТЗ для модели рецептов в админ-зону в списке рецептов
    # нужно вывести название рецепта и автора рецепта
    list_display = ('pk', 'name', 'author')
    # также по ТЗ нужно вывести фильтры по автору, названию рецепта и тегам
    list_filter = ('author', 'name', 'tags')

    # также по ТЗ нужно вывести общее кол-во добавлений этого рецепта
    # в избранное


# для настройки отображения модели Ingredient в админке применяем класс
# AdminModel, который связывается с моделью Ingredient и конфигурирует
# отображение данных этой модели в интерфейсе админки
class IngredientAdmin(admin.ModelAdmin):
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


# для настройки отображения модели RecipeIngredient в админке применяем класс
# AdminModel, который связывается с моделью RecipeIngredient и конфигурирует
# отображение данных этой модели в интерфейсе админки
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')


# для настройки отображения модели Favorite в админке применяем класс
# AdminModel, который связывается с моделью Favorite и конфигурирует
# отображение данных этой модели в интерфейсе админки
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')


# при регистрации модели Recipe источником конфигурации для нее
# назначаем RecipeAdmin
admin.site.register(Recipe, RecipeAdmin)
# при регистрации модели Ingredient в админ-зоне
# источником конфигурации для нее назначенм IngredientAdmin
admin.site.register(Ingredient, IngredientAdmin)
# при регистрации модели Tag в админ-зоне
# источником конфигурации для нее назначенм TagAdmin
admin.site.register(Tag, TagAdmin)
# при регистрации промежуточной модели RecipeIngredient
# источником конфигурации указываем RecipeIngredientAdmin
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
# при регистрации модели Favorite источником конфигурации
# назначим FavoriteAdmin
admin.site.register(Favorite, FavoriteAdmin)
