# from django.shortcuts import render
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from users.models import User

from .serializers import (CreateUserSerializer, IngredientSerializer,
                          ReadRecipeSerializer, ReadUserSerializer,
                          TagSerializer)

# для создания вьюсета для модели User нужно определиться с функционалом
# какой набор действий нас интересует.
# 1. создать пользователя(create)
# 2. получить список пользователя(list)
# 3. получить отедльного пользователя(retrieve)
# т.о наследоваться от класса ModelViewSet будет избыточно -
# т.к.по сути он наследует целый набор миксинов для всех опереций CRUD
# (см. доку)
# поэтому мы можем переопределить свой вьюсет, выбрав только нужные действия
class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    # дальше указываем 2 обязательных поля
    # выборку объектов модели, с которыми будет работать вьюсет
    # это все объекты модели пользователя
    queryset = User.objects.all()
    # далее нужно или установить аттрибут serialiser_class и указать сериализатор для модели
    # или указать аттрибут get_serializer_class - чтобы обеспечить динамическое поведение,
    #  то есть выбрать нужный сериализатор в зависимости от типа запроса
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadUserSerializer
        return CreateUserSerializer

    # далее нам нужно описать нестандартные действия, которые также должны быть маршрутизируемыми.
    # 1. Cменить пароль(эндпоинт - api/users/set_password)
    # 2. Показать текущего пользователя(эндпоинт - api/users/me)
    # 3. Мои подписки(эндпоинт - api/users/subscriptions)
    # 4. Подписаться/отписаться от автора(эндпоинт - api/users/{id}/subscribe)
    # Все эти действия нестандартные, но они должны вызываться при переходе на указанные эндпоинты.
    # Для этих целей напишем отдельные методы для выполнения этих действий
    # и обернем эти метода в декоратор @actions.
    # Этот декоратор настраивает методы, которые в него обернуты и создает эндпоинты для
    # этих действий - то есть, делает эти нестандартные действия маршрутизируемыми.

    # по умолчанию декоратор actions отслеживает только GET-запросы,
    # но если указать парамметр methods, то можно явно указать нужные методы

    # В декораторе можно явным образом указать, должен ли метод работать с одним объектом
    # или с коллекцией объектов.
    # Для этого используется параметр detail,
    # который может принимать значения True (разрешена работа с одним объектом)
    #  или False (работаем с коллекцией).
    @action(detail=False, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        pass

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        pass

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        pass

    @actions(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request):
        pass


# ЧАСТИЧНО ГОТОВО
class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение списка тегов и конкретного тега по его id.
    """
    # В TagViewSet передается запрос в соответствии с адресами,
    # зарегистрированными в роутере
    # router_v1.register('tags', TagViewSet, basename='tags').
    # Этот вюсет должен обрабатывать только GET-запросы:
    # 1. получение списка тегов
    # 2. получение конкретного тега по его идентификатору
    # выбираем для создания вьюсета класс ReadOnlyViewSet
    # Таким образом мы в одном вьюсете можем объединить 2 класса
    # TagList и TagDetail(действия list, retrieve)
    # указываем аттрибуты queryset, serializer_class:
    # в queryset задаем выборку объектов модели,
    # с которой будет работать вьюсет
    # в serializer_class указываем какой сериализатор будет использован
    # для сериализации данных
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


# ЧАСТИЧНО ГОТОВО
class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Получение списка ингредиентов и конкретного ингредиента по его id.
    """
    # В IngredientViewSet передается запрос в соответствии с адресами,
    # зарегистрированными в роутере
    # router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
    # Этот вьюсет(также как в случае с тегами) должен обрабатывать только GET-запросы:
    # 1. получение списка ингредиентов
    # 2. получение конкретного ингредиента по его идентификатору
    # Также выбираем для создания вьюсета класс ReadOnlyViewSet
    # Таким образом мы в одном вьюсете можем объединить 2 класса
    # IngredientList и IngredientDetail(действия list, retrieve)
    # указываем необходимые аттрибуты:
    # в queryset задаем выборку объектов модели, с которой будет работать вьюсет
    # в serializer_class указываем какой сериализатор будет использован для сериализации данных
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer
