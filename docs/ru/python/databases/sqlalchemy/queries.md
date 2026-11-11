
# Запросы, JOIN и выражения SQL

[English](../../../../en/python/databases/sqlalchemy/queries.md)

Откройте страницу, чтобы отфильтровать строки, соединить таблицы или сформировать SQL-выражение.
Полные файлы используют учебные данные общей схемы; PostgreSQL здесь проверяется компиляцией.

[Справочник](README.md) · [Общая схема](models-and-transactions.md#единая-схема-для-рецептов)

| Задача | Приём | Пример |
| --- | --- | --- |
| Написать SELECT/JOIN/CTE | select, aliased, func | [Полный набор запросов](#select-join-подзапросы-и-cte) |
| Устранить N+1 | Выбрать стратегию загрузки | [Карточки отношений](relationship-loading.md) |
| Обработать много строк | yield_per и partitions | [Большие выборки](streaming.md) |
| Проверить PostgreSQL-выражение без сервера | Компиляция выбранным диалектом | [PostgreSQL](#postgresql-компиляция-без-подключения) |

**Уровень:** средний → продвинутый.
Предпосылки: SQL JOIN/агрегация и Session.
Для запуска нужны Python 3.14, SQLAlchemy 2.1.8 и pytest 9.2.0; SQLite входит в Python.
Файлы используют `demo_models.py`.
Установите `sqlalchemy[asyncio]` и `pytest` в отдельное окружение.

- [SELECT, JOIN, подзапросы и CTE](#select-join-подзапросы-и-cte)
- [Проверки результатов](#проверить-результаты-запросов)
- [Загрузка отношений](relationship-loading.md)
- [Большие выборки](streaming.md)
- [PostgreSQL: компиляция без подключения](#postgresql-компиляция-без-подключения)


## SELECT, JOIN, подзапросы и CTE

Полный пример `demo_queries.py` создаёт небольшой набор данных.
Вызывайте `seed()` один раз для каждой пустой базы.

[`sqlalchemy/demo_queries.py`](../../../../../examples/python/databases/sqlalchemy/demo_queries.py)

Запустите `python demo_queries.py`.
Результат содержит двух авторов и два поста Alice.
У Bob руководителем указана Alice.
Количества постов равны `2` и `0`.
Возрастные группы имеют значения `adult`/`minor`.
Выбор нескольких колонок возвращает строки.
`scalars()` оставляет первую колонку.
Если нужны все выбранные значения, не применяйте `scalars()`.


## Проверить результаты запросов

Полный `test_queries.py` проверяет строки, возвращаемые `query_report()`.
Сохраните файл рядом с `demo_models.py` и `demo_queries.py`.

[`sqlalchemy/test_queries.py`](../../../../../examples/python/databases/sqlalchemy/test_queries.py)

Запустите `python -m pytest -q test_queries.py`.
Результат: один тест проходит.
Каждый запуск создаёт отдельную SQLite в памяти.


## Загрузка и большие выборки

Для N+1 и выбора loader откройте [карточки загрузки отношений](relationship-loading.md).
Для чтения по частям откройте [большие выборки](streaming.md).
Полные проверки отношений находятся в [loading-lab.md](loading-lab.md).


## PostgreSQL: компиляция без подключения

**Уровень:** продвинутый.
Полный пример `demo_postgresql_sql.py` только компилирует SQL.
Пример не подключается к PostgreSQL.
Компиляция не подтверждает блокировки, планы или выполнение.

[`sqlalchemy/demo_postgresql_sql.py`](../../../../../examples/python/databases/sqlalchemy/demo_postgresql_sql.py)

Запустите `python demo_postgresql_sql.py`.
Вывод содержит `ON CONFLICT`, `FOR UPDATE`, частичный уникальный индекс и UPDATE с CTE.
UPSERT сначала создаёт insert-объект.
Затем UPSERT использует `excluded` этого объекта.
Ссылка на ещё не присвоенный `stmt` неверна.
Условная уникальность PostgreSQL реализуется частичным **уникальным индексом**, а не `UniqueConstraint(postgresql_where=...)`.
При реальном выполнении эти изменяющие запросы обновят строки или схему.
Блокировка существует только в живой транзакции соответствующей СУБД.

Источники: [PostgreSQL ON CONFLICT и индексы](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html), [SQL выражения](https://docs.sqlalchemy.org/en/21/core/selectable.html).
