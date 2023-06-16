# Дипломный проект Яндекс Практикум:
## Foodgram

![example workflow](https://github.com/RBychin/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)


### - Описание проекта:
- Foodgram - сайт, для обмена рецептами.
  - Пользователи могут создавать рецепты, добавлять их в избранное и в корзину покупок.
  - Пользователи могут подписываться на других пользователей.
  - Организована Админ-панель, Администраторы могут управлять тегами, ингредиентами, рецептами и пользователями.



### - Стек разработки бекенда:
- Работа сайта организована на API запросах от фронтенда к бекенду.

  - Python 3.10
  - Django 4.2.1
  - Django REST Framework 3.14.0
  - PostgreSQL 14.8
  - PyCharm 2023 1.2 (CE)


### - Первичный запуск:

- Скачайте папки `infra` и `data` из корневой директории проекта.
- Разместите эти папки на своем сервере.
- В директории `infra` создайте файл `.env` \
  со следующими данными:
  - `HOST=<http://rbychin.ddns.net> адрес хоста`
  - `DB_ENGINE=django.db.backends.postgresql`
  - `DB_NAME=<Имя базы>`
  - `POSTGRES_USER=<Имя пользователя>`
  - `POSTGRES_PASSWORD=<Пароль базы>`
  - `DB_HOST=infra_db_1`
  - `DB_PORT=5432`

- docker-compose exec backend bash
