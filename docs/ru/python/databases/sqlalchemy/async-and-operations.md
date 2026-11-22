
# Async, события и миграции

[English](../../../../en/python/databases/sqlalchemy/async-and-operations.md)

Откройте страницу, чтобы управлять async-сессией, наблюдать SQL или изменить схему через Alembic.
Все изменяющие примеры используют отдельную учебную SQLite.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Прочитать async-отношение | `awaitable_attrs` либо eager loading | [Async-программа и тесты](#асинхронная-сессия) |
| Наблюдать SQL и транзакции | `event.listen` и снятие обработчиков | [Диагностика](#события-и-диагностика) |
| Изменить схему | Autogenerate, ручная проверка, upgrade | [Отдельный проект Alembic](#alembic-отдельный-учебный-проект) |

[Справочник](README.md) · [Общая схема](models-and-transactions.md)

**Уровень:** продвинутый.
Используйте Python 3.14; установите зависимости выбранного примера перед его запуском.
Предпосылки: транзакции, [основы `asyncio`](../../language/asyncio.md) и различие между изменениями схемы и данных.

- [Асинхронная сессия](#асинхронная-сессия)
- [События и диагностика](#события-и-диагностика)
- [Alembic: отдельный учебный проект](#alembic-отдельный-учебный-проект)


## Асинхронная сессия

Выполните `python -m pip install 'sqlalchemy[asyncio]==2.1.9' 'aiosqlite==0.22.1' 'pytest==9.2.0' 'pytest-asyncio==1.5.0'`.
Ниже приведён полный пример `demo_async.py`.
Возьмите остальные классы из `demo_models.py` этой темы.
Драйвер использует только SQLite в памяти.

[`sqlalchemy/demo_async.py`](../../../../../examples/python/databases/sqlalchemy/demo_async.py)

Запустите `python demo_async.py`.
Результат содержит два списка `['Async Python']`.
Первый список получен через `AsyncAttrs.awaitable_attrs`.
Второй список получен через предварительную загрузку.
Закрывайте сессию и движок через контекст/finally.
В HTTP-приложении используйте lifespan/[зависимости](../../web/fastapi/database.md) для закрытия сессии и движка.
Для `asyncio.gather` каждой конкурентной задаче нужна отдельная сессия.
Не включайте sync-драйвер в `create_async_engine`.

SQLite проверяет внешние ключи только после включения `PRAGMA foreign_keys=ON` на соединении.
Как и sync-фабрика, async-фабрика включает этот режим для каждого нового соединения, включая создание схемы.
Обработчик подключается к `engine.sync_engine`.

Полный `test_async.py`:

[`sqlalchemy/test_async.py`](../../../../../examples/python/databases/sqlalchemy/test_async.py)

Источники: [SQLAlchemy asyncio, AsyncAttrs, implicit I/O](https://docs.sqlalchemy.org/en/21/orm/extensions/asyncio.html), [SQLite foreign keys](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html#foreign-key-support).


## События и диагностика

Используйте `demo_models.py` и [зависимости общей схемы](models-and-transactions.md#единая-схема-для-рецептов).
Для наблюдения SQL не нужны aiosqlite и Alembic.
Полный пример `demo_observe.py` показывает engine event и session events.
Пример удаляет обработчики после работы.
Поэтому повторный запуск не удваивает обработчики.

[`sqlalchemy/demo_observe.py`](../../../../../examples/python/databases/sqlalchemy/demo_observe.py)

Полный `test_observe.py`:

[`sqlalchemy/test_observe.py`](../../../../../examples/python/databases/sqlalchemy/test_observe.py)

Запустите `python -m pytest -q test_observe.py`.
Измеряемое время охватывает выполнение DBAPI cursor.
Измерение не охватывает полный lifecycle HTTP-запроса или все расходы ORM.

| Задача | Приём / ограничение |
| --- | --- |
| SQL-лог | `logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)` после настройки logging либо `create_engine(..., echo=True)` |
| Посмотреть выражение | `str(stmt.compile(engine))`; это не EXPLAIN и не выполнение |
| Session hooks | `before_commit`, `after_commit`, `after_rollback`. После commit не рассчитывайте продолжить SQL в завершённой транзакции |
| Model hooks | `before_insert`, `before_update`, `load`; mapper events имеют ограничения на допустимые действия |
| Параметризованный запрос | `select(User).where(User.id == bindparam("uid"))`, затем параметры отдельно |
| Кэш | Встроенный cache компиляции; он не кэширует результаты и не является серверным prepare |

Фрагменты таблицы требуют импорты и модель из предыдущих примеров.
SQL-логи могут содержать значения параметров.
Если значения чувствительны, используйте `hide_parameters=True`.
Применяйте соответствующую политику логирования.
Для async обработчики событий часто подключают к `engine.sync_engine` / sync Session.
В этом случае обработчик не объявляют как `async def`.

Источники: [events](https://docs.sqlalchemy.org/en/21/core/event.html), [ORM events](https://docs.sqlalchemy.org/en/21/orm/events.html), [cache](https://docs.sqlalchemy.org/en/21/core/connections.html#sql-caching).


## Alembic: отдельный учебный проект

Создайте отдельную пустую папку и виртуальное окружение.
Сохраните [полную общую схему](models-and-transactions.md#единая-схема-для-рецептов) как `demo_models.py` в этой папке.
Extra `asyncio` нужен импорту `AsyncAttrs` из общей схемы, даже для синхронной миграции.
Не указывайте URL существующей пользовательской БД.
Проверка SQLite не подтверждает миграцию других диалектов.

Команды оболочки:

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.9' 'alembic==1.20.1'
alembic init alembic
```

Фрагмент `alembic.ini` для локального учебного файла:

```ini
sqlalchemy.url = sqlite:///training-migrations.db
```

Замените `target_metadata = None` фрагментом `alembic/env.py` ниже.
Сохраните остальную часть сгенерированного файла:

```python
from demo_models import Base

target_metadata = Base.metadata
```

```bash
alembic revision --autogenerate -m "create training schema"
```

Проверьте сгенерированный кандидат.
В этой схеме есть собственный `JSONDict`.
Если Alembic вывел `demo_models.JSONDict()`, добавьте в модуль revision импорт `import demo_models`.
Без импорта применение завершится `NameError`.
Этот шаг относится к ручной проверке autogenerate.
Шаг не меняет `env.py`.

```bash
alembic upgrade head
alembic current
alembic history --verbose
```

`revision` создаёт кандидат миграции.
Прочитайте кандидат перед выполнением.
`upgrade` меняет структуру учебной БД.
Autogenerate не обнаруживает все изменения.
Autogenerate не понимает семантику переименований.
Для следующего шага сначала отредактируйте модель.
Затем создайте новую revision.

Ниже приведён **фрагмент** следующей revision.
Фрагмент добавляет nullable столбец.
Затем фрагмент заполняет существующие строки и ужесточает ограничение через SQLite batch.
Фрагмент требует `from alembic import op` и `import sqlalchemy as sa` в сгенерированном модуле.
Возьмите имена revision/down_revision из реальной цепочки.

```python
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("users", sa.Column("verified", sa.Boolean(), nullable=True))
    op.execute(sa.text("UPDATE users SET verified = false WHERE verified IS NULL"))
    with op.batch_alter_table("users") as batch:
        batch.alter_column("verified", existing_type=sa.Boolean(), nullable=False)


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("verified")
```

Команды изменения версии:

```bash
alembic upgrade +1
alembic downgrade -1
```

`downgrade -1` применит обратную миграцию.
Команда может удалить столбец **вместе с данными**.
Не запускайте команду только ради просмотра истории.
Для конкретной revision укажите её настоящий id.
Значения вроде `abc123` — не готовые команды.
Перед переносом на настоящую БД подготовьте резервную копию.
Проверьте миграцию.
Проверьте откат.
Подготовьте план для ограничений конкретного диалекта.
Async-вариант использует специальный шаблон `alembic init -t async alembic`.
Не оборачивайте обычный `env.py` произвольным `AsyncEngine(...)`.

Источники: [Alembic tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html), [batch для SQLite](https://alembic.sqlalchemy.org/en/latest/batch.html), [async cookbook](https://alembic.sqlalchemy.org/en/latest/cookbook.html#using-asyncio-with-alembic).
