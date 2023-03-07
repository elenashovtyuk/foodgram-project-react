# from django.shortcuts import render
# from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes.models import Ingredient, Recipe, Tag
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from .pagination import CustomPaginator
from .serializers import (CreateRecipeSerializer, CreateUserSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          ReadUserSerializer, SetPasswordSerializer,
                          SubscribeSerialiser, SubscriptionSerialiser,
                          TagSerializer)


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

    # при поступлении GET-запроса для получения текущего пользователя
    # этот запрос поступает в UserViewSet в метод def me,
    # обернутый в декоратор action для маршрутизации нестандартных действий.
    # при поступлении GET-запроса происходит сериализация, в ходе которой
    # пользователь получает данные в формате JSON о текущем пользователе.
    # по умолчанию в UserViewSet Djoser-а этот метод отрабатывает несколько
    # типов запроса.
    # Нам нужен только GET, поэтому указываем его в парамметре methods
    # pagination_class = None отключает пагинацию в этом представлении
    # также укажем permission_classes только для авторизованных пользователей
    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        # сериадлизуем данные пользователя из запроса(request.user)
        serializer = ReadUserSerializer(request.user)
        # возвращаем пользователю сериализованные данные в формате JSON
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    # следующий метод для получения своих подписок
    # запрос может сделать только авторизованный пользователь
    # поэтому указываем permissions=IsAuthenticated
    # так как этот метод будет работать с коллекцией объектов,
    # cо списком подписок, то указываем detail=False
    # также укажем, что этот метод только GET-запросы отрабатывает
    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,),
            pagination_class=CustomPaginator)
    def subscriptions(self, request):
        # выборка пользователей, на которых подписан пользователь из запроса
        queryset = User.objects.filter(subscribing__user=request.user)
        # метод paginate_queryset применяется к полученной выборке
        # и возвращает итерируемый объект
        page = self.paginate_queryset(queryset)
        # дальше создаем экземпляр сериализатора и передаем  в него следующее:
        # page - итерируемый объект, полученный ранее -
        # это выборка пользователей
        # чтобы сериализовать не один объект, а выборку(коллекцию),
        # укажем параметр many=True
        serializer = SubscriptionSerialiser(page, many=True,
                                            context={'request': request})
        # метод get_paginated передается сериализованным данным страницы
        # возвращает объект Response
        return self.get_paginated_response(serializer.data)

    # следующий метод для подписки на автора или отписки от него
    # указываем параметр detail=True, так как этот метод предназначен
    # для работы с одним объектом

    # (подписка/отписка по отношению к одному конкретному автору)
    # далее укажем параметр methods и укажем методы запроса явно,
    #  т.к по умолчанию декоратор action предусматривает только GET-запросы

    # также укажем параметр permission_classes,
    #  так как это действие может выполнять только авторизованный пользователь
    @action(detail=True, methods=('post', 'delete'),
            permission_classes=(IsAuthenticated,))
    # в параметры метода передаем id автора,
    # так как этот параметр нам нужен при получении автора
    def subscribe(self, request, **kwargs):
        """Метод для подписки на определенного автора или отписки."""
        # первое, что нужно сделать -
        # это получить конкретного автора рецепта по его id,
        # чтобы далее уже можно в зависимости от типа запроса
        # подписаться на него или отписаться
        author = get_object_or_404(User, id=kwargs['pk'])
        # пользователя, подписавшегося на автора получаем из запроса
        # request.user
        # далее прописываем логику действий в зависимости от типа запроса
        if request.method == 'POST':
            # если метод POST, то необходима десериализация данных
            # cоздаем экземпляр сериализатора SubscribeSerializer
            # в параметрах передаем  в него объект автора полученного ранее,
            # а также данные из запроса request.data
            # request.data содержит словарь со всеми данными из запроса
            serializer = SubscribeSerialiser(
                author, data=request.data, context={"request": request})
            # далее проверяем валидность полученных данных
            serializer.is_valid(raise_exception=True)
            # в случае валидности создаем экземпляр подписки
            Subscription.objects.create(
                user=request.user,
                author=author)
            # вью-функция должна возвращать объект Response,
            # которому передаются сериализованные данные(это JSON)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

        # если метод DELETE, то мы запрашиваем экземпляр подписки,
        # для которого подписчик - это пользователь из запроса,
        # а автор - это автор, полученный выше по конкретному id
        # (тот автор,которого нужно удалить из подписки).
        # Далее применяем метод delete к полученному экземпляру.
        # если указанный экземпляр не будет найден, то вернется 404.
        if request.method == 'DELETE':
            get_object_or_404(Subscription, user=request.user,
                              author=author).delete()
            # дальше мы должны вернуть сообщение об успешной отписке
            return Response({'detail': 'Успешная отписка'},
                            status=status.HTTP_204_NO_CONTENT)


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


# для описания логики всех действий с ресурсом Рецепты создаем вьюсет
# на основе ModelViewSet, так как этот класс включает весь список операций CRUD.
# list, retrieve, create, update, destroy
class RecipeViewSet(viewsets.ModelViewSet):
    # дальше нужно указать 2 обязательных поля
    # выборку объектов модели, с которыми будет работать вьюсет
    # а также параметр serializer_class или get_serializer_class
    # (для того, чтобы задать динамическое поведение -
    # иметь возможность выбрать нужный сериализатор в зависимости от типа запроса)
    queryset = Recipe.objects.all()

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return CreateRecipeSerializer
    # далее нестандартные действия, которые нужно сделать маршрутизируемыми.
    # для таких действий можно написать отдельные действия задекорировать их
    # @action - этот способ позволяет создать эндпоинты для этих действий
    # 1-ый метод - скачать файл со списком покупок
    @action()
    def download_shopping_cart(self, request):
        pass

    # 2-ой метод - добавить рецепт в список покупок или удалить его из списка
    @action()
    def shopping_cart(self, request):
        pass

    # 3-ий метод - добавить рецепт в избранное или удалить из избранного
    @action()
    def favorite(self, request):
        pass
