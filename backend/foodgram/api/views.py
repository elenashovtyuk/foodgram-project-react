# from django.shortcuts import render
# from django.http import HttpResponse
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import User

from .serializers import (CreateUserSerializer, IngredientSerializer,
                          ReadRecipeSerializer, ReadUserSerializer,
                          TagSerializer, SetPasswordSerializer)


# для создания вьюсета для модели User нужно определиться с функционалом
# какой набор действий нас интересует.
# ОСНОВНЫЕ ДЕЙСТВИЯ:
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

    # далее нужно или установить аттрибут serialiser_class
    # и указать сериализатор для модели
    # или указать аттрибут get_serializer_class -
    # чтобы обеспечить динамическое поведение,
    #  то есть выбрать нужный сериализатор в зависимости от типа запроса
    # ЭТО КАСАТЕЛЬНО ОСНОВНЫХ ДЕЙСТВИЙ ЮЗЕРА (СТАНДАРТНЫХ)
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadUserSerializer
        return CreateUserSerializer

    # далее нам нужно описать НЕСТАНДАРТНЫЕ ДЕЙСТВИЯ,
    # которые также должны быть маршрутизируемыми.
    # 1. Cменить пароль(эндпоинт - api/users/set_password)
    # 2. Показать текущего пользователя(эндпоинт - api/users/me)
    # 3. Мои подписки(эндпоинт - api/users/subscriptions)
    # 4. Подписаться/отписаться от автора(эндпоинт - api/users/{id}/subscribe)
    # Все эти действия нестандартные, но они должны вызываться при переходе
    # на указанные эндпоинты. Этих эндпоинтов пока нет,
    # их нужно каким-то образом создать.
    # Для этих целей напишем отдельные методы для выполнения этих действий
    # и обернем эти методы в декоратор @actions.
    # Этот декоратор настраивает методы, которые в него обернуты и создает
    # эндпоинты для этих действий - то есть,
    # делает эти нестандартные действия маршрутизируемыми.

    # по умолчанию декоратор actions отслеживает только GET-запросы,
    # но если указать парамметр methods, то можно явно указать нужные методы

    # В декораторе можно явным образом указать, должен ли метод работать
    # с одним объектом или с коллекцией объектов.
    # Для этого используется параметр detail,
    # который может принимать значения True (разрешена работа с одним объектом)
    #  или False (работаем с коллекцией).

    # 1-ый нестандартный метод - сменить пароль
    @action(detail=False, methods=('post',),
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        # при поступлении POST-запроса на эндпоинт users/set_password
        # в целях смены пароля, этот запрос будет обрабатываться во вьюсете
        # UserViewSet, конкретно в методе def set_password.
        # Поступившие данные должны пройти десериализацию
        # Поступившие в формате JSON данные c помощью сериализатора
        # SetPasswordSerializer
        # будут преобразованы в простые типы данных Python
        # и затем пройдут валидацию. Если данные будут валидны,
        # то новый пароль будет сохранен.
        # метод is_valid принимает необязательный флаг raise_exception.
        # который заставит его поднять исключение serializers.ValidationError,
        # если есть ошибки валидации (при raise_exception=True)

        # при создании экземпляра сериализатора передаем в него
        #  существующий экземпляр пользователя (request.user),
        # чтобы именно ИЗМЕНИТЬ ЕГО, а не создать новый.
        #  И указываем данные из запроса (request.data)
        # для обновления пользователя
        # (new_pasword и current_password)
        serializer = SetPasswordSerializer(request.user, data=request.data)
        # далее обязательно этап валидации входящих данных
        if serializer.is_valid(raise_exception=True):
            # Далее метод save приведет либо к созданию нового экземпляра,
            # либо к изменению существующего в зависимости от того,
            # был ли передан существующий экземпляр (request.user)
            # при создании экземпляра сериализатора (см выше)
            serializer.save()
            return Response({'detail': 'Пароль успешно изменен!'},
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        pass

    @action(detail=False,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        pass

    @action(detail=True, methods=('post', 'delete'),
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
    # router_v1.register('ingredients', IngredientViewSet,
    # basename='ingredients')
    # Этот вьюсет(также как в случае с тегами) должен обрабатывать
    # только GET-запросы:
    # 1. получение списка ингредиентов
    # 2. получение конкретного ингредиента по его идентификатору
    # Также выбираем для создания вьюсета класс ReadOnlyViewSet
    # Таким образом мы в одном вьюсете можем объединить 2 класса
    # IngredientList и IngredientDetail(действия list, retrieve)
    # указываем необходимые аттрибуты:
    # в queryset задаем выборку объектов модели,
    # с которой будет работать вьюсет
    # в serializer_class указываем какой сериализатор будет использован
    # для сериализации данных
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ReadRecipeSerializer
