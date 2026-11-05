# Конфигурация, БД и развёртывание Flask

Уровень: продвинутый. Предпосылки: factory, контексты Flask, транзакции SQL.
[К справочнику Flask](README.md).

## Конфигурация до запуска

В [factory](application.md) значения по умолчанию загружаются первыми, затем `FLASK_...`
через `from_prefixed_env()`, затем явная тестовая конфигурация.
Переменные окружения предоставляй через систему запуска/secret store; не записывай production-ключи в Git.
`SECRET_KEY` нужен для подписи session cookie. Не храни чувствительные данные в cookie, считая их зашифрованными.

| Настройка | Когда нужна |
| --- | --- |
| `TESTING` | В тестах; не заменяет production config |
| `MAX_CONTENT_LENGTH` | Ограничение тела запроса; согласовать также с proxy |
| `SECRET_KEY` | Непредсказуемый ключ для подписанных сессий; управлять ротацией |
| `SESSION_COOKIE_SECURE` | Cookie только по HTTPS |
| `SESSION_COOKIE_HTTPONLY` | Ограничить доступ browser JS к cookie |
| `SESSION_COOKIE_SAMESITE` | Выбрать политику cross-site; не считать полной CSRF-защитой |
| `TRUSTED_HOSTS` | Ограничить допустимые Host при подходящей архитектуре |

Для расширений создавай объект без app, а внутри factory вызывай `extension.init_app(app)`
после конфигурации. Не заводи один глобальный connection на все запросы/worker.

## Жизненный цикл соединения

Полный дополнительный модуль `flask_db.py`. Создание схемы отделено от открытия соединения;
путь БД задаётся приложением. Запросы с пользовательскими данными параметризуют, а commit выполняют явно.
Закрытие ресурса не должно «случайно коммитить» успешные или ошибочные HTTP-запросы.

<!-- example: flask/flask_db.py -->
```python
import sqlite3

from flask import current_app, g


def get_db():
    if "database" not in g:
        g.database = sqlite3.connect(current_app.config["DATABASE"])
    return g.database


def close_db(error=None):
    connection = g.pop("database", None)
    if connection is not None:
        connection.close()


def init_app(app):
    app.teardown_appcontext(close_db)
```

В factory после загрузки config подключи `flask_db.init_app(app)`. Это приложение использует SQLite
через стандартный `sqlite3`; для SQLAlchemy нужны его собственные границы Session и транзакций.
`g` относится к текущему app context, а не является общим хранилищем между процессами.

Полный проверяемый тест `test_flask_db.py`, рядом с `flask_app.py` и `flask_db.py`:

<!-- example: flask/test_flask_db.py -->
```python
import sqlite3

import pytest

from flask_app import create_app
from flask_db import get_db, init_app


def test_connection_lifecycle_and_rollback(tmp_path):
    path = tmp_path / "demo.sqlite"
    app = create_app({"TESTING": True, "DATABASE": str(path)})
    init_app(app)
    with app.app_context():
        connection = get_db()
        assert get_db() is connection
        connection.execute("CREATE TABLE items (name TEXT NOT NULL)")
        connection.execute("INSERT INTO items VALUES (?)", ("saved",))
        connection.commit()
        connection.execute("INSERT INTO items VALUES (?)", ("rolled back",))
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        connection.execute("SELECT 1")
    with app.app_context():
        next_connection = get_db()
        assert next_connection is not connection
        assert next_connection.execute("SELECT name FROM items").fetchall() == [("saved",)]
```

Запуск: `python -m pytest -q test_flask_db.py`; ожидается **1 passed**.
Тест проверяет повторное использование внутри контекста, закрытие, откат незакоммиченной вставки
и независимость следующего контекста. Создаётся только SQLite-файл во временном каталоге pytest.
Teardown здесь закрывает ресурс независимо от успеха запроса; бизнес-транзакцию оформляй отдельно.
Миграции и production backup в этот пример не входят; см. [SQLAlchemy](../../databases/sqlalchemy/README.md),
[SQLite](../../../databases/relational/sqlite/README.md).

## Разработка и production

`flask run --debug` — встроенный сервер разработки, reloader и debugger. Не используй их для эксплуатации.
Flask — WSGI-приложение; server/hosting выбирается отдельно. Например, Gunicorn на поддерживаемом Unix
или Waitress, если подходит его модель/платформа. Установка сервера и параметры workers/threads
требуют отдельной проверки; ниже только справочная команда, **не выполнялась**:

```text
gunicorn --bind 127.0.0.1:8000 'flask_app:create_app()'
```

Она предполагает установленный Gunicorn и импортируемый `flask_app`.
Производительность и число workers здесь не измерялись. Reverse proxy может выполнять TLS и ограничение запросов;
нужны health checks, тайм-ауты, graceful shutdown и сбор логов.
`ProxyFix` включай только за доверенным proxy с точным числом hops; иначе клиент может подделывать forwarded headers.
Не переноси setup/регистрацию маршрутов на «первый запрос»: каждый worker должен стартовать с одинаковым app.

Async views требуют соответствующей установки Flask и не превращают WSGI worker в ASGI-сервер.
Не запускай долговечную фоновую задачу через `asyncio.create_task()` внутри view: используй отдельный worker/очередь
с определёнными retry и состоянием задачи.

## Источники и границы проверки

[Configuration](https://flask.palletsprojects.com/en/stable/config/),
[database tutorial](https://flask.palletsprojects.com/en/stable/tutorial/database/),
[deploying](https://flask.palletsprojects.com/en/stable/deploying/),
[Gunicorn](https://flask.palletsprojects.com/en/stable/deploying/gunicorn/),
[proxy](https://flask.palletsprojects.com/en/stable/deploying/proxy_fix/),
[async](https://flask.palletsprojects.com/en/stable/async-await/).
2026-11-06: SQLite lifecycle выполнен на Python 3.14.7 / Flask 3.1.3.
Production WSGI, TLS, proxy, migrations, сессии браузера и многопроцессная БД не запускались.
