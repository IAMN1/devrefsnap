# Собрать пакет, внедрить зависимости и проверить сценарий

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
Каждый блок ниже — полный файл по указанному пути внутри новой учебной папки.

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
Все файлы перечислены в блоках.
Инструмент упаковки читает `pyproject.toml`:

<!-- example: project-design/pyproject.toml -->
```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "cheatsheet-catalog-demo"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic==2.14.3", "pydantic-settings==2.16.2"]

[dependency-groups]
dev = ["pytest==9.2.0"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

Версии прикладных зависимостей закреплены для этого примера.
Ограничение Python и выбор build backend не подтверждают все возможные сочетания окружения.
Зафиксируйте полученное окружение проекта, например в `uv.lock`.
Обновляйте окружение осознанно.

Файл `__init__.py` обозначает обычный пакет.
Здесь файл содержит только строку документации:

<!-- example: project-design/src/catalog_demo/__init__.py -->
```python
"""Учебный пакет поиска товаров."""
```

## Модель и сценарий

<!-- example: project-design/src/catalog_demo/domain.py -->
```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    title: str


class ProductNotFound(LookupError):
    pass
```

<!-- example: project-design/src/catalog_demo/application.py -->
```python
from dataclasses import dataclass
from typing import Protocol

from .domain import Product, ProductNotFound


class Catalog(Protocol):
    def get(self, sku: str) -> Product | None:
        ...


@dataclass
class FindProduct:
    catalog: Catalog

    def execute(self, sku: str) -> Product:
        sku = sku.strip()
        if not sku:
            raise ValueError("SKU не должен быть пустым")
        product = self.catalog.get(sku)
        if product is None:
            raise ProductNotFound(sku)
        return product
```

`...` — допустимое тело метода `Protocol`, который описывает интерфейс для статической проверки типов.
Работающие реализации приведены ниже; их поведение проверяют тесты, а не сам `Protocol`.

## Два адаптера

<!-- example: project-design/src/catalog_demo/adapters.py -->
```python
import sqlite3

from .domain import Product


class MemoryCatalog:
    def __init__(self, products: list[Product]):
        self._products = {product.sku: product for product in products}

    def get(self, sku: str) -> Product | None:
        return self._products.get(sku)


class SQLiteCatalog:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def get(self, sku: str) -> Product | None:
        row = self._connection.execute(
            "SELECT sku, title FROM products WHERE sku = ?", (sku,)
        ).fetchone()
        return Product(*row) if row is not None else None
```

Адаптер получает соединение извне.
Адаптер не создаёт скрытое глобальное соединение.
Схема нужна заранее.
Тест создаёт схему явно.
В приложении схему создаёт выбранный механизм миграций.
Значение SKU передаётся параметром SQL, а не подставляется форматированием строки.

## Настройки и сборка

<!-- example: project-design/src/catalog_demo/config.py -->
```python
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CATALOG_DEMO_")
    environment: Literal["development", "test", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
```

Пример не читает `.env` автоматически.
В своём приложении выбирайте источник настроек явно.
Задавайте приоритет настроек явно.
Environment, конкретный `.env`, secret storage и аргументы запуска решают разные задачи.
`BaseSettings` импортируется из **pydantic_settings**, а не из `pydantic` v1.

<!-- example: project-design/src/catalog_demo/bootstrap.py -->
```python
import logging

from .adapters import MemoryCatalog
from .application import FindProduct
from .config import Settings
from .domain import Product


def build_application(settings: Settings) -> FindProduct:
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")
    catalog = MemoryCatalog([Product("book", "Python guide")])
    return FindProduct(catalog)
```

Это composition root — место сборки объектов с известными конкретными реализациями.
Если понадобится SQLite, сборка обеспечит создание соединения.
Сборка также обеспечит закрытие соединения.
Сборка передаст другой адаптер.
Сценарию `FindProduct` менять импорты на sqlite3 не потребуется.

## Запуск

<!-- example: project-design/src/catalog_demo/__main__.py -->
```python
import argparse

from .bootstrap import build_application
from .config import Settings
from .domain import ProductNotFound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sku")
    args = parser.parse_args()
    application = build_application(Settings())
    try:
        product = application.execute(args.sku)
    except (ValueError, ProductNotFound):
        parser.error("Товар не найден или SKU пуст")
    print(f"{product.sku}: {product.title}")


if __name__ == "__main__":
    main()
```

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

<!-- example: project-design/tests/test_catalog.py -->
```python
from contextlib import closing
import sqlite3

import pytest
from pydantic import ValidationError

from catalog_demo.adapters import MemoryCatalog, SQLiteCatalog
from catalog_demo.application import FindProduct
from catalog_demo.config import Settings
from catalog_demo.domain import Product, ProductNotFound


@pytest.fixture(params=["memory", "sqlite"])
def catalog(request):
    if request.param == "memory":
        yield MemoryCatalog([Product("book", "Python guide")])
    else:
        with closing(sqlite3.connect(":memory:")) as connection:
            with connection:
                connection.execute("CREATE TABLE products (sku TEXT PRIMARY KEY, title TEXT NOT NULL)")
                connection.execute("INSERT INTO products VALUES (?, ?)", ("book", "Python guide"))
            yield SQLiteCatalog(connection)


def test_existing_product(catalog):
    assert FindProduct(catalog).execute(" book ") == Product("book", "Python guide")


@pytest.mark.parametrize("sku", ["unknown", "book' OR 1=1 --"])
def test_unknown_product(catalog, sku):
    with pytest.raises(ProductNotFound):
        FindProduct(catalog).execute(sku)


def test_empty_sku(catalog):
    with pytest.raises(ValueError, match="SKU"):
        FindProduct(catalog).execute(" ")


def test_settings_are_validated(monkeypatch):
    monkeypatch.setenv("CATALOG_DEMO_ENVIRONMENT", "test")
    assert Settings().environment == "test"
    with pytest.raises(ValidationError):
        Settings(environment="unrecognized")
```

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
