
# Подготовить блог SQLite и проверить запросы

[English](../../../../en/databases/relational/sqlite/query-lab.md)

Пример проверяет JOIN, параметры, ограничения, каскадное удаление и откат.
БД существует только в памяти и не открывает пользовательские файлы.
[К карточкам запросов](python-and-queries.md) · [К SQLite](README.md).

Нужен Python 3.14 со штатным sqlite3 и SQLite 3.37 или новее для STRICT.


## Полный пример: блог в памяти

Сохраните файл [`demo.py`](../../../../../examples/databases/relational/sqlite/demo.py).
Выполните `python3.14 demo.py`.
Зависимостей из pip нет.
Параметр autocommit=True выбран явно.
SQL-команды BEGIN/COMMIT/ROLLBACK ниже управляют транзакцией.

[`sqlite/demo.py`](../../../../../examples/databases/relational/sqlite/demo.py)

Пример проверяет успешный JOIN.
Пример проверяет отказ для неизвестного пользователя и неверного типа.
Пример также проверяет каскадное удаление и полный откат удаления.
Прочитайте результат RETURNING до фиксации.
`last_insert_rowid()` / cursor.lastrowid относятся к последней соответствующей вставке в соединении.
RETURNING часто яснее связывает id с конкретной командой.


## Источники

- [Python sqlite3 / transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [функции](https://www.sqlite.org/lang_corefunc.html), [даты](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [индексы](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
- [SQLite 3.53.4: release notes](https://www.sqlite.org/releaselog/3_53_4.html).
