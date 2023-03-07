from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from recipes.models import (Ingredient, Tag, Recipe)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from users.models import User, Subscription
from drf_base64.fields import Base64ImageField

# момент с аутентификацией решаем с помощью библиотеки djoser.

# djoser генерирует новые эндпоинты:
# /users/
# /users/me/
# /users/set_password/
# /tokin/login/
# /token/logout/

# для обработки этих эндпоинтов djoser по умолчанию использует
# свои собственные сериализаторы и вьюсеты.
# Если не переопределять сериализаторы, то
# будут по умолчанию применены сериализаторы из библиотеки djoser,
# созданные для сериализации базовой модели User.
# В нашем случае это не подходит, так как у нас используется
# не базовая модель User.
# Мы создавали собственную кастомную модель User на основе AbstractUser и
# поэтому и сериализаторы для этой модели прописываем самостоятельно.

# для нашей кастомной модели напишем следующие сериализаторы:

# Для обработки эндпоинта /users/ пишем 2 разных сериализатора -
# для чтения (получить список пользователей)
# и для записи(создать нового пользователя)

# Для обработки эндпоинта /users/me/ также пишем свой сериализатор.

# Остальные сериализаторы для обработки эндпоинтов /users/set_password/,
# /token/login/, /token/logout/ мы не пишем -
# используем их по умолчанию из библиотеки djoser.

# После создания сериализаторов указываем их в settings.py для Djoser.


# 1-ый сериализатор - для обработки запроса по эндпоинту /users/ -
# для чтения, т.е для получения списка пользователей.
# указываем модель, для которой пишем сериализатор и поля указываем явно.
class ReadUserSerializer(serializers.ModelSerializer):
    """[GET] Сериализатор для модели пользователя(только для чтения)."""

    # для поля is_subscribed указываем типом поля
    # сериализатор SerializerMethodField,
    # так как это поле новое - его нет у модели User,
    # но мы должны получить его на выходе
    # то есть, должна быть информация о подписках
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        pass

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class CreateUserSerializer(serializers.ModelSerializer):
    """
    [POST] Сериализатор для модели пользователя(для записи).
    Создание нового пользователя.
    """
    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate(self, obj):
        invalid_usernames = ['me', 'set_password',
                             'subscriptions', 'subscribe']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Вы не можете использовать этот username.'}
            )
        return obj

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
        }


# создаем сериализатор для смены пароля -
# наследник от Serializer(сериализатор,
# который работает с обычными классами, а не с моделями)
# В этом сериализаторе все поля нужно задавать вручную.
# у нас их два - текущий и новый пароли
class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()
    # НУЖНО СДЕЛАТЬ ВАЛИДАЦИЮ, ЧТО НОВЫЙ ПАРОЛЬ ВЕРНЫЙ И
    #  ЧТО ОН ОТЛИЧЕН ОТ ТЕКУЩЕГО ПАРОЛЯ
    # Валидация может быть на уровне поля и на уровне объекта
    # если требуется осуществить проверку, затрагивающую несколько полей,
    # то тут следует применить ВАЛИДАЦИЮ НА УРОВНЕ ОБЪЕКТА
    # для этого указываем следующий метод

    def validate(self, data):
        # этот метод принимает на вход один единственный аргумент - data
        # словарь значений полей(т.е полей new_password, current_password)
        # для проверки валидации в django.contrib.auth.password_validate
        # существует несколько функций, которые можно вызвать для интеграции
        # проверки пароля в своем коде.
        # используем конструкцию try-except
        # в блок try поместим функцию, которую проверяет пароль
        # (это одна из полезных функций для интеграции валидации из
        # django.contrib.auth.password_validate)
        # в аргументах передаем пароль, который нужно проверить
        # используя обращение по ключу словаря data
        try:
            validate_password(data['new_password'])
        # если проверка идет в штатном режиме, то блок except будет пропущен
        # если же возникает любое исключение,
        # то управление передается в блок except
        except django_exceptions.ValidationError as password_error:
            # в случае какой-то неотработанной ошибки  выбросить raise
            raise serializers.ValidationError(
                {'new_password': list(password_error.messages)}
            )
        return super().validate(data)

    # Далее необходимо указать метод def update
    # для того, чтобы расширить функционал и
    # иметь возможность изменять существующий пароль
    # В этот метод передается ссылка instance на объект, который следует
    # изменить(у нас это current_password) и словарь validated_data
    # с проверенными данными.(полученные выше в методе def validate)
    def update(self, instance, validated_data):
        # используем функцию check_password из
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        # берем из словаря validated_data по ключу данные:
        # current_password(текущий пароль) и по ключу new_password
        # (новый пароль).
        # сравниваем эти значени и если они равны, то возвращаем исключение
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


# ГОТОВО
# создаем сериализатор для модели Ingredient
# эта модель простая, без связей.
# Сериализатор для нее тоже будет простым.
# В классе Meta указываем модель, для которой будет создан сериализатор
# и ЯВНО указываем поля модели, для которых необходима сериализация.
# Так как для модели Ingredient в апи-документации указан один тип запроса
# - GET, то в конструктор сериализатора для модели ингредиента
# поступает экземпляр модели Ingredient или queryset.
# Соответственно будет запущен именно процесс сериализации -
# прямое преобразование сложных данных (экземпляра модели или queryset)
# в простые типы данных Python и их дальнейшее преобразование в JSON-формат
class IngredientSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('name', 'measurement_unit')


# ГОТОВО
# создаем сериализатор для модели Tag
# Это тожем простая модель, без связей.
# сериализатор для нее тоже простой.
# В классе Meta указываем модель, для которой будет создан сериализатор
# и ЯВНО перечисляем поля, для которых необходима сериализация.
# Так как для модели Tag в апи-документации указан только GET-запрос,
# то в конструктор сериализатора для модели тега
#  поступает экземпляр модели Tag.
# Соответственно будет запущен именно процесс сериализации -
# прямое преобразование сложных данных (экземпляра модели или queryset)
#  в простые типы данных Python и их дальнейшее преобразование в JSON-формат
class TagSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели рецептов(только для чтения)."""
    # Этот сериализатор нужно прорабатывать более детально,
    # так как модель рецептов - сложная, со связями.
    # Для этого сериализатора нужно переопределить некоторые поля

    # 1. Модель Recipe связана с моделью User ч/з поле author(ForeignKey).
    # Для поля ForeignKey по умолчанию в сериализаторе будет тип поля
    # PrimaryKeyRelatedField -
    # т.е при GET-запросе рецепта будет получен id автора
    # это не информативно, нам необходимо получить строковое представление.
    # поэтому нам необходимо переопределить тип этого поля
    # Для этого сначала необходимо написать сериализатор для модели User
    # (для чтения)
    # и применить его в качестве типа поля для author в нашем,
    # родительском сериализаторе.
    # То есть, теперь это поле будет возвращать объекты модели User,
    #  сериализованные в ReadUserSerializer.

    # 2. Модель Recipe связана с моделью Tag ч/з поле tags(ManyToManyField).
    # Если мы не переопределим тип этого поля в сериализаторе,
    # то запрашивая рецепт, мы также получим список id тегов
    # а не список самих тегов. Это не информативно.
    # Нужно переопределить тип этого поля.
    # Для этого используем созданный ранее сериализатор для модели Tag.
    # Применяем его в качестве типа поля tags и теперь
    # это поле будет возвращать объекты модели Tag,
    # сериализованные в TagSerializer - то есть,
    # эти данные вернутся в виде JSON.

    # 3. Модель Recipe связана с моделью Ingredient ч/з поле ingredients
    # (ManyToManyField).
    # Если мы не переопределим тип этого поля в сериализаторе,
    # то запрашивая рецепт, мы также получим список id ингредиентов
    # а не список самих ингредиентов. Необходимо переопределить тип поля.
    # Согласно макетам на фронте при запросе рецепта по его id
    # помимо всех прочих полей должен вернуться список ингредиентов
    # (именно ингредиентов, а не id ингредиентов) с указанием их кол-ва.
    # то есть, для этого поля необходимо произвести доп.вычисления,
    # то есть применить свой код для этого поля, модифицировать его.
    # Для этих целей используем SerializerMethodField в качестве типа поля
    # ingredients и далее выполняем вычисления для этого поля

    # 4. Для полей is_favorite и is_in_shopping_cart потребуется применить
    # SerializerMethodField. Этот тип поля применяют,
    # когда во время сериализации определенного поля требуется запустить
    #  какой-то свой код для того, чтобы получить значение этого поля.
    # Также часто при работе с апи требуется в ответе вернуть те поля,
    # которых нет в сериализуемой модели
    # (как раз этих двух полей нет в модели Recipe).
    # То есть, с помощью SerializerMethodField можно модифицировать
    # существующее поле
    # (например произвести какие-то вычисления с ним)
    # или создать новое поле(наш случай с этими 2 полями).
    # при запросе рецепта по этим двум полям должно вернуться булево значение
    # предварительно импортируем этот тип поля из rest-framework.fields.
    # Когда полю присвоен тип SerializerMethodField,
    # то DRF вызывает метод с именем def get <имя этого поля>

    # ИТОГ
    # для 3-ех полей сериализатора ReadRecipeSerializer
    # мы используем SerializerMethodField:
    # для поля ingredients -
    # для того, чтобы модифицировать это поле
    # для полей in_favorite, is_in_shopping_cart -
    #  для того, чтобы создать новые поля, которых нет в модели

    author = ReadUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = SerializerMethodField()
    is_favorite = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    def get_ingredients(self, obj):
        """Выполняет вычисление кол-ва ингредиентов."""

    def get_is_favorite(self, obj):
        """Проверяет, добавил ли пользователь рецепт в избранное."""
        pass

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавил ли пользователь рецепт в список покупок."""
        pass

    class Meta:
        # укажем модель
        model = Recipe
        # укажем поля, для которых необходима сериализация
        # часть этих полей выше будем переопределять
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorite',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


# class CreateRecipeSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели рецептов(для записи)."""
#     author = serializers.StringRelatedField()

#     class Meta:
#         model = Recipe
#         fields = (
#             'author',
#             'tags',
#             'ingredients',
#             'name',
#             'image',
#             'text',
#             'cooking_time'
#         )


# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели ингредиентов в составе рецепта."""
#     class Meta:
#         model = RecipeIngredient
#         fields = ('recipe', 'ingredient', 'amount')


# class FavoriteSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели избранных рецептов."""
#     class Meta:
#         model = Favorite
#         fields = ('user', 'recipe')


# class ShoppingCartSerializer(serializers.ModelSerializer):
#     """Сериализатор для модели списка покупок."""
#     class Meta:
#         model = ShoppingCart
#         fields = ('user', 'recipe', 'add_date')

class RecipeSerializer(serializers.ModelSerializer):
    """Список рецептов без ингридиентов."""
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


# создаем сериализатор для подписок, ДЛЯ ЧТЕНИЯ
class SubscriptionSerialiser(serializers.ModelSerializer):
    """
    [GET] Сериализатор для получения списка авторов,
    на которых подписан пользователь.
    """
    # в классе Meta укажем модель для которой создан сериализатор
    # и явно указываем все поля, которые нужно сериализовать - те поля,
    # которые в формате JSONдолжны вернуться пользователю согласно redoc
    # для некоторых полей необходимо указать SerializerMethodField, так как
    # в ответе требуется вернуть те поля, которых нет в сериализуемой модели
    # это следующие поля - 'is_subscribed'(подписан ли автор, булево значение),
    # 'recipes'(список рецептов от тех авторов, на кого подписан пользователь),
    # 'recipes_count'(кол-во рецептов в подписках).
    # с помощью SerializerMethodField можно модифицировать
    # существующее поле
    # (например произвести какие-то вычисления с ним)
    # или создать новое поле(наш случай с этими 3 полями).
    # переопределяем эти три поля, указыввем тип поля SerializerMethodField
    # Когда полю присвоен тип SerializerMethodField,
    # то DRF вызывает метод с именем def get <имя этого поля>

    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Проверяет - подписан ли пользователь на указанного автора."""
    # obj - это объект сериализации, экземпляр класса User
    # Этот метод сгласно тз должен вернуть True,
    # если данный автор есть в подписках пользователя,
    # или False - если не содержит.
    # То есть, если экземпляр класса Subscriptions в качестве user
    # имеет request.user(пользователя из запроса)
    # а в качестве author имеет obj - сериализуемый объект, то будет True
    # юзера из запроса не можем получить напрямую,
    # сначала нужно получить объект запроса, а из него уже извлечь юзера
        request = self.context.get('request')
        if (request.user.is_anonymous) or (request.user == obj):
            return False
        return (Subscription.objects.filter(
                user=request.user, author=obj).exists())

    def get_recipes(self, obj):
        """Возвращает список рецептов в подписках."""
        # сначала получаем обект запроса и сохраняем его в переменной request
        request = self.context.get('request')
        # затем нужно извлечь параметры запроса - кол-во объектов на странице
        page_size = request.GET.get('page_size')
        # obj- это объект сериализации, экземпляр модели User
        # получаем далее все рецепты пользователя
        # (автора, на которого подписываются)
        recipes = obj.recipes.all()
        # дальше нужно выполнить проверку
        if page_size:
            recipes = recipes[int:(page_size)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов в подписках."""
        return obj.recipes.count()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')


# создаем сериализатор для записи - для подписок/отписок
class SubscribeSerialiser(serializers.ModelSerializer):
    """[POST],[DELETE] Сериализатор для подписки/ отписки."""
    # как видим, не все поля, которые мы указываем
    # в Meta(cогласно redoc) есть в модели.
    # это следующие поля -
    # 'is_subscribed'(подписан ли автор, булево значение),
    # 'recipes'(список рецептов от тех авторов, на кого подписан пользователь),
    # 'recipes_count'(кол-во рецептов в подписках).
    # с помощью SerializerMethodField можно создать новое поле
    # (наш случай с этими 3 полями).
    # Для этих 3-ех полей указыввем тип поля SerializerMethodField.
    # Когда полю присвоен тип SerializerMethodField,
    # то DRF вызывает метод с именем def get <имя этого поля>
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()

    is_subscribed = SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()

    # def validate(self, obj):
    #     if (self.context['request'].user == obj):
    #         raise serializers.ValidationError(
    #             {'errors': 'Ошибка подписки. Нельзя подписаться на себя.'})
    #     return obj

    def get_is_subscribed(self, obj):
        """Проверяет - подписан ли пользователь на указанного автора."""
        # obj - это объект сериализации, экземпляр класса User
        # Этот метод сгласно тз должен вернуть True,
        # если данный автор есть в подписках пользователя,
        # или False - если не содержит.
        # То есть, если экземпляр класса Subscriptions в качестве user
        # имеет request.user(пользователя из запроса)
        # а в качестве author имеет obj - сериализуемый объект, то будет True
        # юзера из запроса не можем получить напрямую,
        # сначала нужно получить объект запроса, а из него уже извлечь юзера
        request = self.context['request']
        if (request.user.is_anonymous) or (request.user == obj):
            return False
        return (Subscription.objects.filter(
                user=request.user, author=obj).exists())

    # def get_recipes(self, obj):
    #     """Возвращает список рецептов в подписках."""
    #     pass

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов в подписках."""
        return obj.recipes.count()

    class Meta:
        # указываем модель, для которой нужна сериализаци/десериализация данных
        model = User
        # также указываем поля, которые должны быть сериализованы
        # перечисляем их явно
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        )
