
# Конфигурация, БД и развёртывание Flask

[English](../../../../en/python/web/flask/configuration-and-deployment.md)

Откройте страницу, чтобы загрузить конфигурацию, закрывать соединение SQLite и выбрать WSGI-запуск.
Пример БД создаёт данные только во временном каталоге теста.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Определить порядок config | Defaults → окружение → тест | [Настройки](#конфигурация-до-запуска) |
| Дать соединению границу контекста | `g` и `teardown_appcontext` | [Модуль и тест](#жизненный-цикл-соединения) |
| Выбрать production-запуск | WSGI server и доверенный proxy | [Развёртывание](#разработка-и-production) |

Уровень: продвинутый. Предпосылки: factory, контексты Flask, транзакции SQL.
[К справочнику Flask](README.md).


## Конфигурация до запуска

В [factory](application.md) первыми загружаются значения по умолчанию.
Затем `from_prefixed_env()` загружает `FLASK_...`.
Последней загружается явная тестовая конфигурация.
Предоставляйте переменные окружения через систему запуска/secret store.
Не записывайте production-ключи в Git.
`SECRET_KEY` нужен для подписи session cookie.
Не храните чувствительные данные в cookie, считая содержимое зашифрованным.

| Настройка | Когда нужна |
| --- | --- |
| `TESTING` | Нужна в тестах. Не заменяет production config |
| `MAX_CONTENT_LENGTH` | Ограничивает тело запроса. Согласуйте лимит также с proxy |
| `SECRET_KEY` | Нужен непредсказуемый ключ для подписанных сессий. Управляйте ротацией |
| `SESSION_COOKIE_SECURE` | Cookie только по HTTPS |
| `SESSION_COOKIE_HTTPONLY` | Ограничьте доступ browser JS к cookie |
| `SESSION_COOKIE_SAMESITE` | Выберите политику cross-site. Не считайте настройку полной CSRF-защитой |
| `TRUSTED_HOSTS` | При подходящей архитектуре ограничьте допустимые Host |

Для расширений создавайте объект без app.
После загрузки конфигурации вызывайте `extension.init_app(app)` внутри factory.
Не создавайте один глобальный connection на все запросы/worker.


## Жизненный цикл соединения

Полный дополнительный модуль `flask_db.py`.
Создание схемы отделено от открытия соединения.
Приложение задаёт путь БД.
Параметризуйте запросы с пользовательскими данными.
Выполняйте commit явно.
Закрытие ресурса не должно «случайно коммитить» успешные или ошибочные HTTP-запросы.

[`flask/flask_db.py`](../../../../../examples/python/web/flask/flask_db.py)

После загрузки config подключите `flask_db.init_app(app)` в factory.
Это приложение использует SQLite через стандартный `sqlite3`.
Для SQLAlchemy нужны собственные границы Session и транзакций.
`g` относится к текущему app context.
`g` не является общим хранилищем между процессами.

Полный проверяемый тест `test_flask_db.py`, рядом с `flask_app.py` и `flask_db.py`:

[`flask/test_flask_db.py`](../../../../../examples/python/web/flask/test_flask_db.py)

Запустите `python -m pytest -q test_flask_db.py`.
Ожидается **1 passed**.
Тест проверяет повторное использование соединения внутри контекста.
Тест проверяет закрытие соединения.
Тест проверяет откат незакоммиченной вставки.
Тест проверяет независимость следующего контекста.
Создаётся только SQLite-файл во временном каталоге pytest.
Teardown здесь закрывает ресурс независимо от успеха запроса.
Оформляйте бизнес-транзакцию отдельно.
Миграции и production backup в этот пример не входят.
Используйте [SQLAlchemy](../../databases/sqlalchemy/README.md) и [SQLite](../../../databases/relational/sqlite/README.md) для этих задач.


## Разработка и production

`flask run --debug` запускает встроенный сервер разработки, reloader и debugger.
Не используйте эти компоненты для эксплуатации.
Flask — WSGI-приложение.
Выбирайте server/hosting отдельно.
Например, можно использовать Gunicorn на поддерживаемом Unix.
Если модель/платформа Waitress подходит, можно использовать Waitress.
Установка сервера и параметры workers/threads требуют отдельной проверки.
Ниже приведена справочная команда.
Для установленного Gunicorn:

```text
gunicorn --bind 127.0.0.1:8000 'flask_app:create_app()'
```

Команда предполагает установленный Gunicorn и импортируемый `flask_app`.
Reverse proxy может обеспечивать TLS и ограничивать запросы.
Нужны health checks, тайм-ауты, graceful shutdown и сбор логов.
Включайте `ProxyFix` только за доверенным proxy с точным числом hops.
Иначе клиент может подделывать forwarded headers.
Не переносите setup/регистрацию маршрутов на «первый запрос».
Каждый worker должен стартовать с одинаковым app.

Async views требуют соответствующей установки Flask и не превращают WSGI worker в ASGI-сервер.
Не запускайте долговечную фоновую задачу через `asyncio.create_task()` внутри view.
Используйте отдельный worker/очередь с определёнными retry и состоянием задачи.


## Источники

[Configuration](https://flask.palletsprojects.com/en/stable/config/),
[database tutorial](https://flask.palletsprojects.com/en/stable/tutorial/database/),
[deploying](https://flask.palletsprojects.com/en/stable/deploying/),
[Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/),
[proxy](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/),
[async](https://flask.palletsprojects.com/en/stable/async-await/).
