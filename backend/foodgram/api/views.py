# from django.shortcuts import render
from django.db.models import Sum
# from django.core import validators
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import FILE
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import RecipeFilter
from .pagination import CustomPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, CreateUserSerializer,
                          IngredientSerializer, ReadRecipeSerializer,
                          ReadUserSerializer, RecipeSerializer,
                          SetPasswordSerializer, SubscribeSerialiser,
                          SubscriptionSerialiser, TagSerializer)


# ГОТОВО
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
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

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
        # user = User.objects.get(pk=request.user.id)
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


# ГОТОВО
class TagViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """
    Получение списка тегов и конкретного тега по его id.
    """
    # В TagViewSet передается запрос в соответствии с адресами,
    # зарегистрированными в роутере
    # router_v1.register('tags', TagViewSet, basename='tags').
    # Этот вюсет должен обрабатывать только GET-запросы:
    # 1. получение списка тегов(list)
    # 2. получение конкретного тега по его идентификатору(retriev)
    # выбираем для создания вьюсета миксины
    # указываем аттрибуты queryset, serializer_class:
    # в queryset задаем выборку объектов модели,
    # с которой будет работать вьюсет
    # в serializer_class указываем какой сериализатор будет использован
    # для сериализации данных
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny, )
    pagination_class = None


# ГОТОВО
class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """
    Получение списка ингредиентов и конкретного ингредиента по его id.
    """
    # В IngredientViewSet передается запрос в соответствии с адресами,
    # зарегистрированными в роутере
    # router_v1.register('ingredients', IngredientViewSet,
    # basename='ingredients')
    # Этот вьюсет(также как в случае с тегами) должен обрабатывать
    # только GET-запросы:
    # 1. получение списка ингредиентов(list)
    # 2. получение конкретного ингредиента по его идентификатору(retrieve)
    # Также выбираем для создания вьюсета миксины только для тех действий
    # которые нам нужны

    # указываем необходимые аттрибуты:
    # в queryset задаем выборку объектов модели,
    # с которой будет работать вьюсет
    # в serializer_class указываем какой сериализатор будет использован
    # для сериализации данных
    # задаем также разрешение на уровне представления - для всех
    # пагинация при выводе списка ингредиентов не нужна, так что None
    # задаем возможность поиска по имени
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (filters.SearchFilter, )
    search_fields = ('^name', )


# для описания логики всех действий с ресурсом Рецепты создаем вьюсет
# на основе ModelViewSet,
# так как этот класс включает весь список операций CRUD.
# и нам нужны практически все - list, retrieve, create, update, destroy
class RecipeViewSet(viewsets.ModelViewSet):
    # дальше нужно указать 2 обязательных поля
    # выборку объектов модели, с которыми будет работать вьюсет
    # а также параметр serializer_class или get_serializer_class
    # (для того, чтобы задать динамическое поведение -
    # иметь возможность выбрать нужный сериализатор в зав-ти от запроса)
    queryset = Recipe.objects.all()
    # настраиваем права доступа на уровне представления
    # используем свой кастомный перимшн
    permission_classes = (IsAuthorOrReadOnly, )
    # настраиваем фильтрацию
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    #filterset_fields = ['is_in_shopping_cart', 'is_favorited']
    # указываем возможные методы
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']
    pagination_class = CustomPaginator

    # укажем метод get_serializer_class для выбора нужного сериализатора
    # в зависимости от типа запроса
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadRecipeSerializer
        return CreateRecipeSerializer

    # далее нестандартные действия, которые нужно сделать маршрутизируемыми.
    # для таких действий можно написать отдельные действия задекорировать их
    # @action - этот способ позволяет создать эндпоинты для этих действий
    # 1-ый метод - скачать файл со списком покупок
    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request, **kwargs):

        # в переменной ingredients сохраняем выборку экземпляров
        # RecipeIngredient из тех рецептов в списке покупок,
        # у которых пользователь добавивший их в список покупок
        # - это пользователь из запроса
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__carts__user=request.user)


            # далее нужно сгруппировать по имени ингредиента
            # и для этих сгруппированных по имени ингредиентов
            # уже будет выполнено сложение из кол-ва
            .order_by('ingredient__name')


            # далее к этой выборке применяем метод values
            # использование этого метода позволяет при выборке вернуть не все
            # экземпляры модели RecipeIngredient целиком со всеми полями,
            # а только нужные поля
            # для дальнейшего суммирования именно по этому полю
            # используем related_name,
            # чтобы для ингредиента в рецепте из связанной таблицы вытащить название и ед.изм
            .values('ingredient__name', 'ingredient__measurement_unit')


            # далее с помощью метода annotate вызываем агрегирующую функцию Sum
            # чтобы просуммировать ингредиенты из полученной выборки
            # агрегирующую функцию Sum импортируем из django.db.models
            .annotate(result_sum_ingr=Sum('amount'))


            # метод values_list позволяет вернуть информацию
            # по указнному выше полю ингредиентв нужном виде -
            # в виде кортежа из значений полей экземпляра ingredient
            .values_list(
                'ingredient__name',
                'result_sum_ingr',
                'ingredient__measurement_unit')
        )


        # далее создаем пустой список, куда будет записан перечень ингредиентов
        list_of_ingredients = []

        # далее применяем метод списка .append - list.append(item)
        # он добавляет элемент, указанный в скобках в конец списка,
        # к которому этот метод применен - то есть, в наш пустой список
        # и в качестве значения, которое надо добавить в этот список
        # укажем строки, к которым применено форматирование
        # с помощью метода format
        # внутри нам требуется передать несколько аргументов -
        # это поля экземпляра модели RecipeIngredient,
        # которые мы выводим выше в values_list
        # соответственно для каждого такого экземпляра
        # мы осуществляем распаковку
        [list_of_ingredients.append(
            '{} - {} {}.'.format(*ingredient)) for ingredient in ingredients]


        # данные, которые нужно вернуть пользователю необходимо передать
        #  в конструктор HttpResppnse
        # для вывода ответа используем строковый метод join
        # с его помощьюмы можем объединить в 1 строку элементы списка
        # list_of_ingredients
        # где 'Cписок покупок:\n' + '\n' - это разделитель между элементами
        # \n - перевод каретки на новую строку
        # т.е выводим "Список покупок" -> переходим на новую строку
        # и далее выводим строку, которая объединяет элементы списка
        # и каждый элемент выводит с новой строки(/n)
        # content_type:
        # MIME-тип ответа, устанавливает HTTP-заголовок Content-Type.
        # Если этот параметр не установлен, то применяется mime-тип text/html
        # и значение настройки DEFAULT_CHARSET, то есть в итоге будет:
        # "text/html; charset=utf-8".
        file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(list_of_ingredients),
            content_type='text/plain, charset=utf8')


        # Чтобы браузер обрабатывал ответ как вложение файла,
        #  установим заголовки Content-Disposition
        # заголовок ответа Content-Disposition представляет собой заголовок,
        # указывающий, будет ли контент отображаться встроенным в браузере,
        # то есть как веб-страница, или как часть веб-страницы,
        # или как вложение , которое загружается и сохраняется локально.
        # параметр attachment указывает, что файл должен быть именно загружен
        # большинство браузеров представляют диалоговое окно «Сохранить как»,
        # предварительно заполненное со значением параметров filename если они есть).
        # у нас указан filename = FILE
        # его мы импортируем из settings.py
        file['Content-Disposition'] = (f'attachment; filename={FILE}')
        return file

    # 2-ой метод - добавить рецепт в список покупок или удалить его из списка
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, **kwargs):
        # для ресурса ShoppingCart возможны 2 типа запросов
        # POST и DELETE
        # при POST запросе определенный рецепт добавляем в список покупок
        #  т.е создаем экземпляр модели ShoppingCart
        # где user - пользователь из объекта запроса,
        # recipe - конкретный рецепт из БД, выбранный по его id
        # при DELETE-запросе определенный рецепт удаляется из списка покупок
        # т.е выбирается и удаляется конкретный экземпляр модели ShoppingCart

        # первое, что нужно сделать - получить конкретный рецепт по его id
        # если такого нет в базе, то вернется ошибка 404
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        # дальше в зависимости от типа запроса предпринимаются нужные действия
        # по отношению к полученному рецепту
        if request.method == 'POST':
            # если метод POST, то необходим процесс десериалиции
            # для этого создаем экземпляр сериализатора
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            # далее проверяем валидность полученных данных
            # в случае валидности создаем экземпляр списка покупок
            # нужно учесть, что данный рецепт возможно уже добавлен
            # в список покупок, это нужно предварительно проверить.
            # если такого рецепта у пользователя нет в списке,
            # т.е нет такого экземпляра модели ShoppingCart, то мы его создаем
            serializer.is_valid(raise_exception=True)
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
                # вью-функция должна возвращать объект Response,
                # которому передаются сериализованные данные(это JSON)
                # и статус выполнения операции
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            # если же метод запроса DELETE,
            #  то нужно удалить указанный экземпляр списка покупок
            # для этого опять же используем метод get_object_or_404
            get_object_or_404(
                ShoppingCart,
                recipe=recipe,
                user=request.user).delete()
            return Response({'detail': 'Рецепт удален из списка покупок'},
                            status=status.HTTP_204_NO_CONTENT)

    # 3-ий метод - добавить рецепт в избранное или удалить из избранного
    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, **kwargs):
        # возможны 2 типа запросов по ресурсу Избранное(Favorite)
        # POST и DELETE
        # при POST-запросе создаем новый экземпляр модели Favorite
        # где user-пользователь из запроса (request.user)
        # а recipe - конкретный рецепт, полученный по id с помощью метода
        # get_object_or_404

        # первое, что нужно сделать - получить конкретный рецепт по его id
        # если такого нет в базе, то вернется ошибка 404
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        # дальше в зависимости от типа запроса предпринимаются нужные действия
        if request.method == 'POST':
            # если метод POST, то необходим процесс десериалиции
            # для этого создаем экземпляр сериализатора
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            # далее проверяем валидность полученных данных
            # в случае валидности создаем экземпляр модели избранное.
            # нужно учесть, что данный рецепт возможно уже добавлен в избранное
            # это нужно проверить
            # если такого рецепта у пользователя нет в избранном,
            # т.е нет такого экземпляра модели Favorite, то мы его создаем
            serializer.is_valid(raise_exception=True)
            if not Favorite.objects.filter(user=request.user,
                                           recipe=recipe).exists():
                Favorite.objects.create(user=request.user, recipe=recipe)
                # вью-функция должна возвращать объект Response,
                # которому передаются сериализованные данные(это JSON)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            # в противном случае возвращаем ошибку.
            return Response({'errors': 'Рецепт уже добавлен в избранное.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            # если же метод запроса DELETE,
            #  то нужно удалить указанный экземпляр избранного
            # для этого опять же используем метод get_object_or_404

            get_object_or_404(
                Favorite,
                recipe=recipe,
                user=request.user).delete()
            return Response({'detail': 'Рецепт удален из избранного'},
                            status=status.HTTP_204_NO_CONTENT)
