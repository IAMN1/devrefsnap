# Типы, настройки и интеграции

Откройте страницу, чтобы проверить список без модели-обёртки, загрузить настройки или перенести Pydantic v1.
Выбирайте Core Schema только при необходимости собственного низкоуровневого типа.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Проверить список или generic | `TypeAdapter`, `Page[T]` | [Типы и полные тесты](#generic-typeadapter-и-собственный-тип) |
| Загрузить окружение | `pydantic-settings.BaseSettings` | [Настройки](#настройки-приложения) |
| Проверить query-параметры | `Annotated[Filters, Query()]` | [FastAPI](#query-модель-fastapi) |
| Перенести v1 или оценить скорость | Migration guide и одинаковые операции | [Миграция и измерения](#миграция-и-производительность) |

[Справочник](README.md) · [Основные модели](models.md)

**Уровень:** средний → продвинутый.
Предпосылки: generics, `Annotated`, переменные окружения.
Core Schema нужна только для низкоуровневых расширений.

- [Generic, TypeAdapter и собственный тип](#generic-typeadapter-и-собственный-тип)
- [Настройки приложения](#настройки-приложения)
- [Query-модель FastAPI](#query-модель-fastapi)
- [Миграция и производительность](#миграция-и-производительность)

## Generic, TypeAdapter и собственный тип

Для воспроизведения используйте Python 3.14.7.
Выполните `python -m pip install 'pydantic==2.14.3' 'pytest==9.2.0' 'pydantic-settings==2.16.2' 'fastapi==0.162.0' 'httpx2==2.16.0'`.
Сохраните полный пример как `demo_advanced.py`.
Возьмите файл `demo_types.py` с [предыдущей страницы](models.md#атрибуты-конфигурация-и-типы).

<!-- example: pydantic/demo_advanced.py -->
```python
import re
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler, TypeAdapter, create_model
from pydantic_core import core_schema

from demo_types import UserView

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1)


class Slug(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler):
        return core_schema.no_info_after_validator_function(cls.check, handler(str))

    @classmethod
    def check(cls, value: str):
        if not re.fullmatch(r"[a-z][a-z0-9-]*", value):
            raise ValueError("Ожидается slug из строчных латинских букв, цифр и дефиса")
        return cls(value)


class Article(BaseModel):
    slug: Slug


class Flexible(BaseModel):
    model_config = ConfigDict(extra="allow")
    metadata: dict[str, Any] = Field(default_factory=dict)


Label = create_model("Label", name=(str, ...), weight=(int, 0))
user_list = TypeAdapter(list[UserView])


if __name__ == "__main__":
    users = user_list.validate_python([{"id": 1, "name": "Alice"}])
    print(Page[UserView](items=users, total=1, page=1, per_page=10).model_dump_json())
    print(Article(slug="python-guide").model_dump_json())
```

Ожидаются JSON страницы пользователей и `{"slug":"python-guide"}`.
Пример создаёт `TypeAdapter` один раз для повторного использования.
Для простого slug достаточно `Annotated[str, Field(pattern=...)]`.
Отдельный класс показан для интеграций, которым нужен собственный Python-тип.
Хук Core Schema чувствителен к обновлениям API.
Закрепите версию.
Проверяйте JSON Schema.
Проверяйте сериализацию.
Одной проверки создания объекта недостаточно.

Полный `test_advanced.py`:

<!-- example: pydantic/test_advanced.py -->
```python
import pytest
from pydantic import ValidationError

from demo_advanced import Article, Flexible, Label, Page, user_list
from demo_types import UserView


def test_page_adapter_and_dynamic_model():
    users = user_list.validate_json('[{"id":1,"name":"Alice"}]')
    page = Page[UserView](items=users, total=1, page=1, per_page=10)
    assert page.items[0].id == 1
    assert Label(name="book").weight == 0
    assert Flexible(source="demo").model_dump()["source"] == "demo"
    with pytest.raises(ValidationError):
        user_list.validate_python([{"id": "not-int", "name": "Alice"}])


def test_custom_type_validation_and_schema():
    article = Article(slug="python-guide")
    assert article.model_dump(mode="json") == {"slug": "python-guide"}
    assert Article.model_json_schema()["properties"]["slug"]["type"] == "string"
    with pytest.raises(ValidationError):
        Article(slug="Wrong slug")
```

## Настройки приложения

Зависимость: `pydantic-settings`.
Полный пример `demo_settings.py` читает только переменные с учебным префиксом.
Пример не подключается к БД.

<!-- example: pydantic/demo_settings.py -->
```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHEATSHEET_PYDANTIC_", case_sensitive=False,
        env_file=None, extra="ignore",
    )
    app_name: str = "Training"
    database_url: str
    api_key: SecretStr | None = None
```

Полный `test_settings.py` использует только синтетическое окружение:

<!-- example: pydantic/test_settings.py -->
```python
import pytest
from pydantic import ValidationError

from demo_settings import Settings


def test_settings_environment_and_required_value(monkeypatch):
    monkeypatch.delenv("CHEATSHEET_PYDANTIC_DATABASE_URL", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    monkeypatch.setenv("CHEATSHEET_PYDANTIC_DATABASE_URL", "sqlite:///training.db")
    monkeypatch.setenv("CHEATSHEET_PYDANTIC_API_KEY", "training-key")
    settings = Settings(_env_file=None)
    assert settings.database_url == "sqlite:///training.db"
    assert settings.api_key.get_secret_value() == "training-key"
    assert "training-key" not in str(settings)
```

Для отдельного учебного dotenv-файла передайте `Settings(_env_file="training.env", _env_file_encoding="utf-8")`.
Значения окружения имеют приоритет над dotenv.
Если вы вызываете `get_secret_value()` и печатаете результат, не полагайтесь на маскирование `SecretStr`.
[Документация settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).

## Query-модель FastAPI

Зависимости: `fastapi`, `httpx2`, `pytest`.
Ниже приведён полный пример `demo_query.py`.
Вызов `Query()` явно задаёт заполнение модели из URL, а не из body.

<!-- example: pydantic/demo_query.py -->
```python
from typing import Annotated

from fastapi import FastAPI, Query
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class Filters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    q: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


@app.get("/items")
def items(query: Annotated[Filters, Query()]):
    return query.model_dump()
```

Полный `test_query.py`:

<!-- example: pydantic/test_query.py -->
```python
from fastapi.testclient import TestClient

from demo_query import app


def test_query_model():
    with TestClient(app) as client:
        assert client.get("/items", params={"q": "python"}).json() == {"q": "python", "limit": 10, "offset": 0}
        assert client.get("/items", params={"q": "python", "limit": 0}).status_code == 422
        assert client.get("/items").status_code == 422
```

Запустите `python -m pytest -q` из папки со всеми файлами темы.
[Источник FastAPI](https://fastapi.tiangolo.com/tutorial/query-param-models/).
Остальные HTTP-задачи находятся в [справочнике FastAPI](../../web/fastapi/README.md).

## Миграция и производительность

| v1 | v2 |
| --- | --- |
| `class Config`, `orm_mode` | `model_config = ConfigDict(from_attributes=True)` |
| `allow_population_by_field_name` | Для новых конфигураций v2.11+: `validate_by_name=True`, `validate_by_alias=True` |
| `dict()` / `json()` | `model_dump()` / `model_dump_json()` |
| `parse_obj()` / `parse_raw()` для JSON | `model_validate()` / `model_validate_json()` |
| `validator` / `root_validator` | `field_validator` / `model_validator` с пересмотром порядка и аргументов |
| `BaseSettings` в pydantic | `pydantic_settings.BaseSettings` |

Совместимый namespace — `pydantic.v1`.
Отдельный пакет `pydantic-v1` для этого не нужен.
Для автоматизации миграции используйте утилиту `bump-pydantic`.
Запускайте утилиту в отдельной ветке.
Проверяйте diff.
Запускайте тесты.
Утилита не подтверждает сохранение поведения.
Без явно проверенного преобразования не смешивайте v1/v2 модели внутри одной структуры.
На Python 3.14 не считайте старую v1-ветку рабочим путём без проверки её ограничений.

Для измерения сравнивайте одинаковые данные и операции через `timeit.repeat`.
Отделяйте построение `TypeAdapter` от повторной валидации.
Фиксируйте версии.
Фиксируйте число повторов.
`model_validate_json` часто избавляет от промежуточного `json.loads`.
Выигрыш зависит от валидаторов и данных.
`model_construct()` не гарантирует ускорение.
Метод пропускает проверки.
Например, `UserView.model_construct(id="wrong", name="Alice")` сохранит невалидный id.
Это поясняющий фрагмент для `demo_types.py`.
Не используйте фрагмент как входной путь.

Источники: [свои типы](https://docs.pydantic.dev/latest/concepts/types/), [TypeAdapter](https://docs.pydantic.dev/latest/concepts/type_adapter/), [generic и create_model](https://docs.pydantic.dev/latest/concepts/models/), [migration guide и bump-pydantic](https://docs.pydantic.dev/latest/migration/), [performance](https://docs.pydantic.dev/latest/concepts/performance/).
