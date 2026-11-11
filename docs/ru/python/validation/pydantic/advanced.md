
# Типы, настройки и интеграции

[English](../../../../en/python/validation/pydantic/advanced.md)

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
Каждый пример ниже имеет собственные зависимости; установите только пакеты выбранной задачи.


## Generic, TypeAdapter и собственный тип

Для воспроизведения используйте Python 3.14.
Выполните `python -m pip install 'pydantic==2.14.3' 'pytest==9.2.0'`.
Сохраните полный пример как `demo_advanced.py`.
Возьмите файл `demo_types.py` с [предыдущей страницы](models.md#атрибуты-конфигурация-и-типы).

[`pydantic/demo_advanced.py`](../../../../../examples/python/validation/pydantic/demo_advanced.py)

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

[`pydantic/test_advanced.py`](../../../../../examples/python/validation/pydantic/test_advanced.py)


## Настройки приложения

В отдельном окружении выполните `python -m pip install 'pydantic-settings==2.16.2' 'pytest==9.2.0'`.
Полный пример `demo_settings.py` читает только переменные с учебным префиксом.
Пример не подключается к БД.

[`pydantic/demo_settings.py`](../../../../../examples/python/validation/pydantic/demo_settings.py)

Полный `test_settings.py` использует только синтетическое окружение:

[`pydantic/test_settings.py`](../../../../../examples/python/validation/pydantic/test_settings.py)

Для отдельного учебного dotenv-файла передайте `Settings(_env_file="training.env", _env_file_encoding="utf-8")`.
Значения окружения имеют приоритет над dotenv.
Если вы вызываете `get_secret_value()` и печатаете результат, не полагайтесь на маскирование `SecretStr`.
[Документация settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/).


## Query-модель FastAPI

В отдельном окружении выполните `python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'`.
Ниже приведён полный пример `demo_query.py`.
Вызов `Query()` явно задаёт заполнение модели из URL, а не из body.

[`pydantic/demo_query.py`](../../../../../examples/python/validation/pydantic/demo_query.py)

Полный `test_query.py`:

[`pydantic/test_query.py`](../../../../../examples/python/validation/pydantic/test_query.py)

Запустите только нужный модуль: `python -m pytest -q test_advanced.py`, `test_settings.py` или `test_query.py`.
Для вывода JSON выполните `python demo_advanced.py` из учебной папки этого примера.
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
