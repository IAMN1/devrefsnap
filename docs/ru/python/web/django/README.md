# Django

[English](../../../../en/python/web/django/README.md)

Django связывает модели Python с базой данных и предоставляет встроенную админку для работы с записями. В этом примере вы добавите учебную книгу в локальную базу SQLite и проверите результат тестами.

| Задача | Приём | Пример |
| --- | --- | --- |
| Описать книгу и создать таблицу | `models.Model`, `migrate` | [Модель и миграция](#модель-и-миграция) |
| Добавить книгу через браузер | `admin.site.register`, `createsuperuser` | [Админка](#админка) |
| Проверить доступ и сохранение | `TestCase`, `manage.py test` | [Тесты](#тесты) |

## Подготовка

Учебный проект находится в `examples/python/web/django`. Команды проекта выполняет [`manage.py`](../../../../../examples/python/web/django/manage.py).
Для запуска нужны Python 3.14 и Django 5.2.19 из ветки 5.2 LTS. Версия Django задана в [`requirements.txt`](../../../../../examples/python/web/django/requirements.txt). SQLite доступна через модуль Python `sqlite3`.

В терминале macOS или Linux перейдите из корня репозитория в каталог примера. Создайте виртуальное окружение. Активируйте окружение перед установкой зависимостей.

```bash
cd examples/python/web/django
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Остальные команды выполняйте из этого каталога в активном окружении.

## Модель и миграция

[Модель `Book`](../../../../../examples/python/web/django/catalog/models.py) описывает книгу с полем `title`. [Начальная миграция](../../../../../examples/python/web/django/catalog/migrations/0001_initial.py) описывает создание таблицы для этой модели. [Настройки проекта](../../../../../examples/python/web/django/config/settings.py) подключают приложение `catalog` и задают файл базы `db.sqlite3`.

Примените миграции из примера. Проверьте состояние миграции приложения `catalog`.

```bash
python manage.py migrate
python manage.py showmigrations catalog
```

На первом запуске `migrate` создаёт файл `db.sqlite3` и таблицы, в том числе таблицы для пользователей и книг. В выводе `showmigrations` должна появиться строка `[X] 0001_initial`.

Если вы изменили модель, создайте новую миграцию.

```bash
python manage.py makemigrations catalog
```

Откройте созданный файл миграции и проверьте список операций. Если миграция удаляет поле, применение удалит столбец и его значения. Примените проверенную миграцию к учебной базе.

```bash
python manage.py migrate
```

## Админка

[Регистрация `Book`](../../../../../examples/python/web/django/catalog/admin.py) добавляет форму и список книг во встроенную админку. [Маршрут проекта](../../../../../examples/python/web/django/config/urls.py) подключает админку по адресу `/admin/`.

Создайте учебного суперпользователя. При запросе имени и пароля укажите данные для этого примера. Поле электронной почты можно оставить пустым.

```bash
python manage.py createsuperuser
```

Запустите сервер разработки на локальном адресе. Используйте настройки примера и `runserver` только для локальной разработки с учебными данными.

```bash
python manage.py runserver 127.0.0.1:8000
```

1. Откройте [админку](http://127.0.0.1:8000/admin/). Войдите под созданной учётной записью.
2. Откройте `Books`. Нажмите `Add book`.
3. В поле `Title` введите `Demo Book`.
4. Нажмите `Save`. Книга `Demo Book` появится в списке.

Остановите сервер сочетанием `Ctrl+C`.

## Тесты

Проверьте, есть ли изменения моделей без миграций. Затем запустите [тесты админки](../../../../../examples/python/web/django/catalog/tests.py).

```bash
python manage.py makemigrations --check --dry-run
python manage.py test catalog
```

Первая команда выводит `No changes detected`. Вторая команда запускает два теста и выводит `OK`.

Первый тест проверяет, что анонимный посетитель попадает на страницу входа при попытке открыть форму добавления книги. Второй тест отправляет форму от имени суперпользователя и проверяет сохранение книги. `force_login()` создаёт сеанс суперпользователя без проверки пароля.

Django запускает тесты без `runserver` и создаёт отдельную базу SQLite в памяти. Книга, которую вы добавили вручную, остаётся в `db.sqlite3`.

## Источники

- [Django 5.2. Модель, миграции и админка](https://docs.djangoproject.com/en/5.2/intro/tutorial02/)
- [Django 5.2. Команды `manage.py`](https://docs.djangoproject.com/en/5.2/ref/django-admin/)
- [Django 5.2. Запуск тестов и тестовая база](https://docs.djangoproject.com/en/5.2/topics/testing/overview/)
- [Django 5.2. Тестовый клиент и `force_login()`](https://docs.djangoproject.com/en/5.2/topics/testing/tools/#the-test-client)
- [Примечания к выпуску Django 5.2.19](https://docs.djangoproject.com/en/5.2/releases/5.2.19/)
