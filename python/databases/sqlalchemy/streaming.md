# Обработать большую выборку по частям

Откройте страницу, если нужно ограничить число одновременно создаваемых ORM-объектов при чтении результата.
Выбор загрузки отношений описан [отдельно](relationship-loading.md).
[Справочник](README.md) · [Схема моделей](models-and-transactions.md#единая-схема-для-рецептов).

| Ситуация | Приём | Пример |
| --- | --- | --- |
| Нужно читать результат партиями | `yield_per` и `partitions()` | [Карточка обработки](#читать-результат-партиями) |
| Вместе с родителями нужны коллекции | Проверить совместимость loader и драйвера | [Таблица ограничений](#совместить-с-загрузкой-отношений) |
| Нужно повторить проверки | Учебная SQLite и pytest | [Полный файл тестов](#проверить-обработку-и-несовместимые-сочетания) |

| Параметр | Значение |
| --- | --- |
| Уровень | Продвинутый |
| Предпосылки | Session, итераторы; demo_models.py и demo_queries.py из [подготовки](loading-lab.md#подготовить-примеры) |
| Зависимости | Python 3.14, SQLAlchemy 2.1.8 и SQLite; [подготовка](loading-lab.md#подготовить-примеры) |

## Читать результат партиями

**Ситуация:** нужно обработать пользователей без сборки всего результата в список.
Фрагмент использует подготовленный `engine` из [учебного набора](loading-lab.md#подготовить-примеры):

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from demo_models import User

with Session(engine) as session:
    result = session.scalars(
        select(User).order_by(User.id).execution_options(yield_per=100)
    )
    for batch in result.partitions():
        for user in batch:
            print(user.name)
```

**Результат учебных данных:** выводятся `alice` и `bob`.
`100` — размер партии в этом фрагменте, а не универсальная настройка.
Не вызывайте `.all()`: метод снова собирает весь результат в память.
Не складывайте обработанные объекты в общий список без необходимости.
Поведение курсора и буферизация драйвера влияют на расход памяти.
[Полная проверка](#проверить-обработку-и-несовместимые-сочетания) использует размер партии `1` для проверки границ.

## Совместить с загрузкой отношений

| Сочетание | Применение | Ограничение |
| --- | --- | --- |
| `yield_per` без eager-коллекций | Поэлементная или пакетная обработка | Не гарантирует предел памяти всего приложения |
| `yield_per` + `selectinload` | Возможно при поддержке независимых курсоров драйвером | Вторичные запросы выполняются по партиям; число SELECT может вырасти |
| `yield_per` + `joinedload` коллекции | Несовместимо | ORM требует накопления строк для коллекции |
| `yield_per` + `subqueryload` коллекции | Несовместимо | Выберите другую организацию чтения |
| `yield_per` + `Result.unique()` | Несовместимо | Unique хранит набор встреченных идентичностей |

В SQLite-примере `selectinload` с партиями проверен.
Это не подтверждает поддержку тех же курсоров другим драйвером.
Для N+1 сначала [выберите состав загрузки](relationship-loading.md#выбрать-стратегию).
Затем отдельно проверьте пакетную обработку на нужной СУБД и драйвере.

## Проверить обработку и несовместимые сочетания

Полный `test_streaming.py` использует те же модели и исходный `seed()`.
Сохраните файл рядом с `demo_models.py` и `demo_queries.py`.
Установите `sqlalchemy[asyncio]==2.1.8` и `pytest==9.2.0` в отдельное окружение.
Фикстура создаёт и освобождает SQLite в памяти для каждого теста.

<!-- example: sqlalchemy/test_streaming.py -->
```python
import pytest
from sqlalchemy import select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload

from demo_models import User, new_engine
from demo_queries import seed


@pytest.fixture
def engine():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
        yield engine
    finally:
        engine.dispose()


def test_partitions_preserve_all_names(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).order_by(User.id).execution_options(yield_per=1))
        names = []
        for batch in result.partitions():
            assert len(batch) == 1
            names.extend(user.name for user in batch)
        assert names == ["alice", "bob"]


def test_selectin_with_partitions_on_sqlite(engine):
    with Session(engine) as session:
        result = session.scalars(
            select(User).options(selectinload(User.posts)).order_by(User.id)
            .execution_options(yield_per=1)
        )
        observed = [(user.name, len(user.posts)) for batch in result.partitions() for user in batch]
        assert observed == [("alice", 2), ("bob", 0)]


@pytest.mark.parametrize("loader", [joinedload, subqueryload])
def test_collection_loaders_reject_yield_per(engine, loader):
    with Session(engine) as session:
        with pytest.raises(InvalidRequestError):
            session.scalars(
                select(User).options(loader(User.posts)).execution_options(yield_per=1)
            ).all()


def test_unique_rejects_yield_per(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).execution_options(yield_per=1))
        with pytest.raises(InvalidRequestError):
            list(result.unique())
```

Запустите `python -m pytest -q test_streaming.py`.
**Результат:** все проверки проходят.
Список `names` в тесте нужен только для проверки полного результата; рабочая карточка обрабатывает объекты сразу.
Исключения проверяют несовместимость сочетаний, а не результат нагрузочного теста.

## Источники

- [ORM yield_per и ограничения](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#fetching-large-result-sets-with-yield-per), [буферизация и server-side cursors](https://docs.sqlalchemy.org/en/21/core/connections.html#using-server-side-cursors-a-k-a-stream-results).
- [Release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
