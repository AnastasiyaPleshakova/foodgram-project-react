# **Продуктовый помощник**

https://pleshakova.hopto.org/admin/

![workflow status badge](https://github.com/AnastasiyaPleshakova/foodgram-project-react/actions/workflows/foodgram-project-react_workflow.yml/badge.svg)

### **Описание:**
Реализован программный интерфейс API для сервиса "Продуктовый помощник". 

"Продуктовый помощник" - это сайт, на котором пользователи могут публиковать рецепты, добавлять рецепты других пользователей в избранное и подписываться на публикации авторов.
С помощью сервиса «Список покупок» у пользователя появилась возможность создавать и скачивать список продуктов, которые необходимы для приготовления понравившихся блюд.

Теперь вы можете интегрировать ваше приложение с текущим, что позволит сэкономить время и ресурсы.

---
### **Ресурсы:**
* Ресурс **auth**: аутентификация.
* Ресурс **users**: пользователи и подписки.
* Ресурс **recipes**: рецепты, которые можно публиковать, изменять, добавлять в избранное и список покупок.
* Ресурс **ingredients**: ингредиенты для приготовления блюд.
* Ресурс **tags**: теги, определяющие тип блюда.

---
### **Роли:**
* **Аноним** — может регистрироваться, авторизироваться и восстанавливать пароль. Просматривать список рецептов или конкретную публикацию.
* **Аутентифицированный пользователь** (user) — может реализовывать весь функционал анонима, а также публиковать рецепты, редактировать и удалять их. Подписываться на других авторов, добавлять рецепты в избранное, добавлять рецепты в список покупок и скачивать данный список в формате pdf.
* **Администратор** (admin) — полные права на управление всем контентом проекта. Может изменять пароли пользователей.
---
### **Технологии:**
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)

---

### **Запуск приложения в контейнерах:**

Клонируйте репозиторий с помощью командной строки:
```
git clone https://github.com/...
```
Перейдите в директорию, где находится файл "docker-compose.yaml":
```
cd ...
```
Запустите docker-compose:
```
docker-compose up -d
```
Создайте миграции:
```
docker-compose exec web python manage.py makemigrations
```
Выполните миграции:
```
docker-compose exec web python manage.py migrate
```
Создайте суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```
Соберите статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```
Заполните базу начальными данными:
```
docker-compose exec web python manage.py load_data
```
Готово:

http://localhost/admin/

---
### **Примеры:**
```
GET-запрос к эндпоинту /api/recipes/ - получение списка всех рецептов
```
```
POST-запрос к эндпоинту /api/recipes/<recipe_id>/favorite - добавление рецепта в избранное
```
```
POST-запрос к эндпоинту /api/recipes/<recipe_id>/shopping_cart/ - добавление рецепта в список покупок
```
```
POST-запрос к эндпоинту /api/recipes/download_shopping_cart/ - скачивание списка покупок
```
```
POST-запрос к эндпоинту /api/users/subscriptions/ - получение списка подписок
```
Внимание! Для доступа к эндпоинтам некоторых типов запросов необходимо зарегистрироваться и получить токен.

---
### **Шаблон наполнения env-файла:**
```
DB_ENGINE=django.db.backends.postgresql

DB_NAME=postgres

POSTGRES_USER=postgres

POSTGRES_PASSWORD=postgres

DB_HOST=db

DB_PORT=5432
```
---
### **ReDoc:**
http://127.0.0.1/redoc/
### **Автор (студент 47 когорты):**

Плешакова Анастасия
