from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from django.db import transaction
from drf_base64.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from users.models import Subscription, User


class ReadUserSerializer(serializers.ModelSerializer):
    """[GET] Сериализатор для модели пользователя(только для чтения)."""

    is_subscribed = serializers.SerializerMethodField()

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

    def get_is_subscribed(self, obj):
        if self.context.get('request') and (
            not self.context['request'].user.is_anonymous
        ):
            return Subscription.objects.filter(
                user=self.context['request'].user, author=obj).exists()
        return False


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


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()

    def validate(self, data):

        try:
            validate_password(data['new_password'])
        except django_exceptions.ValidationError as password_error:
            raise serializers.ValidationError(
                {'new_password': list(password_error.messages)}
            )
        return super().validate(data)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class IngredientSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели ингредиентов."""
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели тегов."""
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода информации об ингредиентах в составе рецепта.
    Выводит список ингредиентов с указанием их кол-ва и ед.изм.
    """
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id',
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Ингредиент и количество для создания рецепта."""
    id = serializers.IntegerField(
        source='ingredient_id',
        required=True
    )
    amount = serializers.IntegerField(
        required=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ReadRecipeSerializer(serializers.ModelSerializer):
    """[GET]Сериализатор для модели рецептов(только для чтения)."""
    author = ReadUserSerializer(
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True
    )
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        source='recipe_to_ingredient'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(
        required=True
    )

    def get_is_favorited(self, obj):
        """Проверяет, добавил ли пользователь рецепт в избранное."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and (Favorite.objects.filter(
                user=request.user, recipe=obj).exists())
        )

    def get_is_in_shopping_cart(self, obj):
        """Проверяет, добавил ли пользователь рецепт в список покупок."""
        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )


class CreateRecipeSerializer(serializers.ModelSerializer):
    """[POST], [PATCH], [DELETE]
    Сериализатор для модели рецептов(для записи, изменения и удаления).
    """
    author = ReadUserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(
        source='ingredient_to_recipe',
        many=True
    )
    image = Base64ImageField(required=True)

    def validate(self, obj):

        if Recipe.objects.filter(name=obj['name']):
            raise serializers.ValidationError('Такой рецепт уже существует.')

        for field in ['name', 'text', 'cooking_time']:
            if not self.initial_data.get(field):
                raise serializers.ValidationError(
                    f'{field} - Обязательное для заполнения поле.'
                )
        if not self.initial_data.get('tags'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 тег.'
            )
        if not self.initial_data.get('ingredients'):
            raise serializers.ValidationError(
                'Нужно указать минимум 1 ингредиент.'
            )
        inrgedient_id_list = [
            item['id'] for item in self.initial_data.get('ingredients')]
        unique_ingredient_id_list = set(inrgedient_id_list)
        if len(inrgedient_id_list) != len(unique_ingredient_id_list):
            raise serializers.ValidationError(
                'Ингредиенты должны быть уникальными.'
            )
        return obj

    @staticmethod
    def ingredient_tag_in_recipe(recipe, ingredients, tags):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(
                    id=ingredient.get('ingredient_id')),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get('request')
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_to_recipe')
        recipe = Recipe.objects.create(author=request.user,
                                       **validated_data)
        self.ingredient_tag_in_recipe(recipe, ingredients, tags)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredient_to_recipe')
        if tags:
            recipe.tags.clear()
        if ingredients:
            recipe.ingredients.clear()
        self.ingredient_tag_in_recipe(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time'
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('name', 'image')
            )
        ]

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance,
                                    context=self.context).data


class RecipeSerializer(serializers.ModelSerializer):
    """Cписок рецептов без ингридиентов.
    Выводится после добавления рецепта в избранное или в список покупок.
    """
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionSerialiser(serializers.ModelSerializer):
    """
    [GET] Сериализатор для получения списка авторов,
    на которых подписан пользователь.
    """
    is_subscribed = SerializerMethodField()
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    def get_is_subscribed(self, obj):
        """Проверяет - подписан ли пользователь на указанного автора."""
        request = self.context.get('request')
        if (request.user.is_anonymous) or (request.user == obj):
            return False
        return (Subscription.objects.filter(
                user=request.user, author=obj).exists())

    def get_recipes(self, obj):
        """Возвращает список рецептов в подписках."""

        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[int:(limit)]
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


class SubscribeSerialiser(serializers.ModelSerializer):
    """[POST],[DELETE] Сериализатор для подписки/ отписки."""

    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    def validate(self, data):
        """
        Проверка уникальности подписки и невозможности подписаться на себя.
        """
        if (self.context['request'].user == self.instance):
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя.'})

        if Subscription.objects.filter(user=self.context['request'].user,
                                       author=self.instance).exists():
            raise serializers.ValidationError(
                {'errors': 'Такая подписка уже существует.'})
        return data

    def get_is_subscribed(self, obj):
        """Проверяет - подписан ли пользователь на указанного автора."""

        request = self.context['request']
        if (request.user.is_anonymous) or (request.user == obj):
            return False
        return (Subscription.objects.filter(
                user=request.user, author=obj).exists())

    def get_recipes_count(self, obj):
        """Возвращает кол-во рецептов в подписках."""
        return obj.recipes.count()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count'
        )
