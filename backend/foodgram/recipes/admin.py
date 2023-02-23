from django.contrib import admin

# Регистрируем модель Recipe
# сначала импортируем ее из нашего модуля models.py
from .models import Recipe


class RecipeAdmin(admin.ModelAdmin):
    # перечисляем поля, которые должны отображаться в админке
    # по ТЗ для модели рецептов в админ-зону в списке рецептов
    # нужно вывести название рецепта и автора рецепта
    list_display = ('pk', 'name', 'author')
    # также по ТЗ нужно вывести фильтры по автору, названию рецепта и тегам
    list_filter = ('author', 'name', 'tags')
    # также по ТЗ нужно вывести общее кол-во добавлений этого рецепта
    # в избранное


# при регистрации модели Recipe источником конфигурации для нее
# назначаем RecipeAdmin
admin.site.register(Recipe, RecipeAdmin)
