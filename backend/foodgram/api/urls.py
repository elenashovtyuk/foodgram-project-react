from django.urls import include, path
from rest_framework.routers import DefaultRouter
# импортируем все вьюсеты из нашего приложения api
from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet
# т.к нам нужно получить коллекцию ссылок на все ресурсы API, то
# нам понадобится стандартный роутер DefaultRouter
# он в отличие от второго базового класса SimpleRouter
# генерирует корневой эндпоинт /,
# GET-запрос к которому вернёт список ссылок на все ресурсы, доcтупные в API.
# создаем экземпляр этого роутера
router = DefaultRouter()

# 2. для того, чтобы роутер создал необходимый набор эндпоинтов
# для наших вьюсетов необходимо вызвать метод register,
# зарегистрировать эндпоинты
# для этого в качестве аргументов метода register укажем следующие аргументы
# URL-префикс(маска) и название вьюсета,
# для которого создается набор эндпоинтов
router.register(r'users', UserViewSet, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

# после регистрации эндпоинтов нужно включить новые эндпоинты в urlpatterns
# все зарегистрированные в routers пути доступны в router.urls
urlpatterns = [
    path('', include(router.urls)),
    path(r'auth/', include('djoser.urls.authtoken'))
]
