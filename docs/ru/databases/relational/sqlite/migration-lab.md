
# Проверить перестроение таблицы SQLite

[English](../../../../en/databases/relational/sqlite/migration-lab.md)

Откройте страницу, если изменение схемы требует создания и замены таблицы.
Пример сохраняет известные индекс, триггер и внешний ключ в синтетической БД.
[К карточкам миграции и WAL](backup-and-migrations.md) · [К SQLite](README.md).

Нужны Python 3.14 со SQLite 3.37 или новее для STRICT и понимание внешних ключей и транзакций.


## Полный пример: перестроение таблицы

Сохраните пример как `migration.py`.
Выполните `python3.14 migration.py`.
Зависимости входят в стандартную библиотеку Python.
Скрипт создаёт и затем удаляет только собственный временный каталог с синтетической БД.
Перед изменением своей схемы получите [проверенную резервную копию](backup-and-restore.md#проверить-восстановленную-бд).

Пример перестраивает известную таблицу и заменяет её в одной транзакции.
Пример не переносит произвольную схему с неизвестными views/triggers автоматически.
Удаление таблицы ниже касается только созданной учебной БД.

[`sqlite/migration.py`](../../../../../examples/databases/relational/sqlite/migration.py)

**Результат:** пользователь получает имя `alice-updated`, триггер сохраняет запись аудита.
Внешняя ссылка и индекс сохраняются.
Новый CHECK отклоняет пустое имя.
Для произвольной схемы дополнительно сохраните и скорректируйте views, triggers и другие зависимости.
Следуйте официальной [процедуре перестроения](https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes).
Включите копирование данных и замену таблицы в одну транзакцию.


## Источники

- [Изменение схемы](https://www.sqlite.org/lang_altertable.html), [транзакции](https://www.sqlite.org/lang_transaction.html), [foreign_keys](https://www.sqlite.org/pragma.html#pragma_foreign_keys).
- [WAL](https://www.sqlite.org/wal.html), [integrity_check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign_key_check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check).
- [Release notes 3.53.4](https://www.sqlite.org/releaselog/3_53_4.html).
