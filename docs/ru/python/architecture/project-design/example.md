
# Собрать пакет, внедрить зависимости и проверить сценарий

[English](../../../../en/python/architecture/project-design/example.md)

Пример ищет товар по SKU в памяти или SQLite.
Используйте пример, чтобы собрать устанавливаемый пакет и проверить один сценарий с двумя способами хранения.

| Нужно вспомнить | Приём | Код / запуск |
| --- | --- | --- |
| Заменить хранение без изменения поиска | Передайте объект с методом `get` | [Сценарий](#модель-и-сценарий), [два адаптера](#два-адаптера) |
| Создать зависимости в одном месте | Соберите объекты перед запуском | [Настройки и сборка](#настройки-и-сборка) |
| Проверить успех, отсутствие товара и неверный вход | Выполните одинаковые тесты для адаптеров | [Тесты](#тесты), [команды](#запуск) |

[К руководству](README.md) · [Объяснение структуры](structure-and-decisions.md)

| Параметр | Значение |
| --- | --- |
| Уровень | Средний: пакет/DI/конфигурация; продвинутый: проверка двух адаптеров |
| Предпосылки | Python, `pyproject.toml`, pytest; для запуска показан uv |

Для запуска используйте Python 3.14 и uv.
Зависимости заданы в `pyproject.toml` ниже.

Пример ограничен поиском товара через CLI; HTTP и запись в производственную БД здесь не реализованы.
Каждая ссылка ведёт к полному файлу примера.


## Навигация

- [Метаданные и структура](#метаданные-и-структура)
- [Модель и сценарий](#модель-и-сценарий)
- [Два адаптера](#два-адаптера)
- [Настройки и сборка](#настройки-и-сборка)
- [Запуск](#запуск)
- [Тесты](#тесты)
- [Как развивать пример](#как-развивать-пример)


## Метаданные и структура

Создайте `src/catalog_demo/` и `tests/`.
До запуска сохраните все файлы из дерева в указанных папках, включая [`tests/test_catalog.py`](../../../../../examples/python/architecture/project-design/tests/test_catalog.py).
Инструмент упаковки читает `pyproject.toml`.

[`project-design/pyproject.toml`](../../../../../examples/python/architecture/project-design/pyproject.toml)

Версии прикладных зависимостей закреплены для этого примера.
Ограничение Python и выбор build backend не подтверждают все возможные сочетания окружения.
Зафиксируйте полученное окружение проекта, например в `uv.lock`.
Обновляйте окружение осознанно.

Файл `__init__.py` обозначает обычный пакет.
Здесь файл содержит только строку документации:

[`project-design/src/catalog_demo/__init__.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/__init__.py)


## Модель и сценарий

[`project-design/src/catalog_demo/domain.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/domain.py)

[`project-design/src/catalog_demo/application.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/application.py)

`...` — допустимое тело метода `Protocol`, который описывает интерфейс для статической проверки типов.
Работающие реализации приведены ниже; их поведение проверяют тесты, а не сам `Protocol`.


## Два адаптера

[`project-design/src/catalog_demo/adapters.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/adapters.py)

Адаптер получает соединение извне.
Адаптер не создаёт скрытое глобальное соединение.
Схема нужна заранее.
Тест создаёт схему явно.
В приложении схему создаёт выбранный механизм миграций.
Значение SKU передаётся параметром SQL, а не подставляется форматированием строки.


## Настройки и сборка

[`project-design/src/catalog_demo/config.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/config.py)

Пример не читает `.env` автоматически.
В своём приложении выбирайте источник настроек явно.
Задавайте приоритет настроек явно.
Environment, конкретный `.env`, secret storage и аргументы запуска решают разные задачи.
`BaseSettings` импортируется из **pydantic_settings**, а не из `pydantic` v1.

[`project-design/src/catalog_demo/bootstrap.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/bootstrap.py)

Это composition root — место сборки объектов с известными конкретными реализациями.
Если понадобится SQLite, сборка обеспечит создание соединения.
Сборка также обеспечит закрытие соединения.
Сборка передаст другой адаптер.
Сценарию `FindProduct` менять импорты на sqlite3 не потребуется.


## Запуск

[`project-design/src/catalog_demo/__main__.py`](../../../../../examples/python/architecture/project-design/src/catalog_demo/__main__.py)

Запустите команды из корня учебного пакета:

```bash
uv sync --group dev
uv run python -m catalog_demo book
uv run pytest -q
```

Первый вызов устанавливает пакет **в учебной папке**.
Этот вызов также создаёт окружение и lock-файл **в учебной папке**.
Поиск выводит `book: Python guide`.
`uv run python -m catalog_demo unknown` заканчивается кодом `2` и сообщением argparse.
Значение `CATALOG_DEMO_ENVIRONMENT=test` допустимо.
При неизвестном имени окружения Settings отклоняет значение до сборки приложения.


## Тесты

[`project-design/tests/test_catalog.py`](../../../../../examples/python/architecture/project-design/tests/test_catalog.py)

Одни и те же проверки выполняются для обоих адаптеров.
SQLite работает в памяти.
После теста соединение SQLite закрывается.
Тест с похожим на SQL значением проверяет параметризацию.
Тесты не затрагивают глобальные данные и настоящие БД.


## Как развивать пример

- HTTP-адаптер переводит `ProductNotFound` в выбранный ответ API. Доменная ошибка не импортирует FastAPI/Flask.
- Задавайте публичную модель ответа на границе приложения. Задавайте права на границе приложения. Задавайте валидацию внешнего JSON на границе приложения.
- Для PostgreSQL понадобятся собственные интеграционные тесты. Успешный тест SQLite не заменяет тесты PostgreSQL.
- Запись данных потребует явной границы транзакции и правил конкурентности. Этот read-only пример не моделирует запись.
- Контейнер DI нужен при реальной пользе для графа и областей жизни. Ручная сборка здесь достаточна.

Источники: [PyPA: pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/),
[Python sqlite3](https://docs.python.org/3.14/library/sqlite3.html), [PEP 544](https://peps.python.org/pep-0544/),
[Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).
