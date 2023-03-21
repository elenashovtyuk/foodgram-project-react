# <div align="center"> Foodgram «Продуктовый помощник» </div>
Онлайн-сервис и API для него. Пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Особенности:

- Просматривать рецепты
- Добавлять рецепты в избранное
- Добавлять рецепты в список покупок
- Создавать, удалять и редактировать собственные рецепты
- Скачивать список покупок

Временно доступен по [адресу](http://51.250.111.182/)

## Используемые технологии

- Python 3.7
- Django 3.2.18
- Django Rest Framework 3.14.0
- Gunicorn 20.1.0
- Nginx 1.19.3
- Postres 13.0-alpine
- Docker 20.10.23
- Docker Compose 2.15.1
- Postman (графическая программа для тестирования API)


## Запуск проекта на локальном компьютере

### Клонируем проект

Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/elenashovtyuk/foodgram-project-react.git

### Cоздаем и активируем виртуальное окружение

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

```
source venv/bin/activate
```

### Установим зависимости

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

### Переходим в папку с файлом docker-compose.yaml

```
cd infra
```
### Запустим проект в контейнерах, находясь в директории с docker-compose.yaml

```
docker-compose up -d --build
```

### Выполним миграции

```
docker compose exec backend python manage.py migrate
```

### Создаем суперпользователя

```
docker compose exec backend python manage.py createsuperuser
```

### Собираем все статические файлы в папку static

```
docker-compose exec backend python manage.py collectstatic --no-input
```

### Загружаем тестовые данные(список ингредиентов)
```
docker compose exec backend python manage.py runscript load_ingredients
```

## Подготовка сервера и запуск проекта на сервере

### Выполним вход на удаленный сервер

### Установим Docker на сервер

```
sudo apt install docker.io
```

### Установим docker-compose на сервер

```
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Отредактируем конфигурационный файл infra/nginx.conf - в строке server_name укажем публичный IP своего сервера

### Отредактируем файл settings.py - добавим в ALLOWED_HOST публичный IP своего сервера или доменное имя

### Скопируем файл docker-compose.yaml на сервер.

```
scp ./docker-compose.yml <username>@<host>:/home/<username>/
```

### Скопируем конфигурационный файл infra/nginx.conf на сервер

```
scp ./nginx.conf <username>@<host>:/home/<username>/default.conf
```

### Cоздадим и заполним файл .env по следующему шаблону:

 - DB_ENGINE=django.db.backends.postgresql
 - DB_NAME=postgres
 - POSTGRES_USER=postgres
 - POSTGRES_PASSWORD=postgres
 - DB_HOST=db
 - DB_PORT=5432
 - DJANGO_SECRET_KEY=<секретный ключ проекта django>

### Соберем контейнеры на удаленном сервере
```
sudo docker-compose up -d --build
```

### Выполнить миграции, собрать статику, создать суперпользователя
```
sudo docker compose exec backend python manage.py migrate

sudo docker compose exec backend python manage.py collectstatic

sudo docker compose exec backend python manage.py createsuperuser
```

### Загрузить ингредиенты в базу данных
```
sudo docker compose exec backend python manage.py runscript load_ingredients
```


### Endpoints:
```
POST /api/users/ - регистрация
POST /api/auth/token/login - создание токена
POST /api/auth/token/logout/ - удаление токена
GET /api/users/ - просмотр информации о пользователях

POST /api/users/set_password/ - изменение пароля
GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

POST /api/recipes/ - создать рецепт
GET /api/recipes/ - получить рецепты
GET /api/recipes/{id}/ - получить рецепт по id
DEL /api/recipes/{id}/ - удалить рецепт по id

GET /api/recipes/{id}/favorite/ - добавить рецепт в избранное
DEL /api/recipes/{id}/favorite/ - удалить рецепт из избранного

GET /api/users/{id}/subscribe/ - подписаться на пользователя
DEL /api/users/{id}/subscribe/ - отписаться от пользователя

GET /api/ingredients/ - получить список всех ингредиентов

GET /api/tags/ - получить список всех тегов

GET /api/recipes/{id}/shopping_cart/ - добавить рецепт в корзину
DEL /api/recipes/{id}/shopping_cart/ - удалить рецепт из корзины
```
