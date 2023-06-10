# Дипломный проект Яндекс Практикум
###### - stage 1 ineration 1

### - Описание проекта:
Foodgram - сайт, для обмена рецептами.
- Пользователи могут создавать рецепты, добавлять их в избранное и в корзину покупок.
- Пользователи могут подписываться на других пользователей.
- Организована Админ-панель, Администраторы могут управлять тегами, ингредиентами, рецептами и пользователями.



### - Стек разработки бекенда:
Работа сайта организована на API запросах от фронтенда к бекенду.

- Python 3.10
- Django 4.2.1
- Django REST Framework 3.14.0
- PostgreSQL 14.8
- PyCharm 2023 1.2 (CE)


### - Запуск:

- Разверните виртуальное окружение в директории `backend` - `python -m venv venv`.
- Активируйте env `source venv/bin/activate`.
- В директории backend находится файл зависимостей `requirements.txt`, \
    установите зависимости `pip install -r requirements.txt`.
- Перейдите в главную директорию проекта (где находится файл `manage.py`) \
    выполните миграции `python manage.py migrate`.
- В репозитории так же есть файл для наполнения базы ингредиентами, он находится в директории `data/ingredients`\
    в проекте предусмотрена команда для наполнения базы. \
    Выполните `python manage.py load_data`, сообщение в консоли проинформирует об успешном завершении импорта.
- В этой же директории необходимо создать `.env` файл для доступа к вашей БД со следующими полями:
  - `DB_ENGINE=django.db.backends.postgresql`
  - `DB_NAME=<Имя вашей базы>`
  - `POSTGRES_USER=<Пользователь базы>`
  - `POSTGRES_PASSWORD=<Пароль для доступа к базе>`
  - `DB_HOST=<IP на котором запущен Postgres>`
  - `DB_PORT=5432 (или другой)`

  В противном случае проект запустится со стандартными настройкам (`sqlite3`).
- Выполните команду `python manage.py runserver` для запуска сервера.\
    Сообщение в консоли проинформирует вас о том, на каком движке запустилась База Данных.
    