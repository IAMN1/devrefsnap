
# Подключение, схема и запросы SQLite

[English](../../../../en/databases/relational/sqlite/python-and-queries.md)

Откройте страницу для подключения, параметров, схемы и запросов SQLite из Python.
Короткий пример работает в памяти; ограничения типов и транзакций зависят от версии библиотеки.


## Быстрый поиск

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Получить строки по пользовательскому значению | Параметры execute | [Короткий пример](#передать-значение-параметром) |
| Проверить связи и откат на готовой схеме | FK, STRICT и явная SQL-транзакция | [Полный блог](query-lab.md#полный-пример-блог-в-памяти) |
| Выбрать тип или проверить индекс | Affinity, STRICT, функции и план | [Типы и функции](#типы-функции-и-индексы) |
| Связать несколько изменений | autocommit и явные BEGIN/ROLLBACK | [Транзакции](#транзакция-в-приложении) |
| Осмотреть БД в терминале или другом языке | CLI и драйвер соответствующего языка | [Подключение](#cli-и-другие-языки) |

[К SQLite](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — подключение/CRUD; средний — ограничения/индексы/транзакции |
| Предпосылки | Python 3.14 со штатным sqlite3; SQLite 3.37+ для STRICT |

<a id="полный-пример-блог-в-памяти"></a>


## Передать значение параметром

**Когда:** нужно получить строки по пользовательскому значению и не подставлять значение в текст SQL.
Ниже — полный короткий пример Python 3.14 без пакетов из pip.
Сохраните блок как `lookup.py` и запустите `python3.14 lookup.py`.

```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:", autocommit=True)) as db:
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL)")
    db.execute("INSERT INTO users VALUES (?, ?)", (1, "alice"))
    rows = db.execute("SELECT id FROM users WHERE username = ?", ("alice",)).fetchall()
    print(rows)
```

**Результат:** `[(1,)]`; файл БД не создаётся.
Параметры передают значения; имена таблиц и столбцов задавайте отдельно контролируемым выбором.
`closing` закрывает соединение; один `with db:` соединение не закрывает.
[Полный блог: подготовка и проверки JOIN, FK/STRICT, RETURNING, CASCADE и rollback](query-lab.md#полный-пример-блог-в-памяти).


## Типы, функции и индексы

**Средний уровень.** Классы хранения — NULL, INTEGER, REAL, TEXT, BLOB.
Affinity столбца — рекомендация преобразования, а не отдельный класс хранения.
В STRICT допустимы INT/INTEGER/REAL/TEXT/BLOB/ANY.
BOOLEAN, DATETIME и JSON не являются допустимыми именами типов STRICT.
Булевы значения можно хранить как 0/1 с CHECK.
Время можно хранить согласованным текстом UTC или числом.
JSON можно хранить как TEXT с подходящей валидацией.
REAL даёт двоичное приближение и не обеспечивает фиксированную десятичную арифметику.

Самостоятельный SQL-фрагмент без таблиц, SQLite:

```sql
SELECT substr('Hello', 2, 3) AS part,
       round(3.14159, 2) AS rounded,
       date('2026-11-06', '+1 day') AS tomorrow,
       json_extract('{"name":"Ada"}', '$.name') AS name;
```

Результат — `ell | 3.14 | 2026-11-07 | Ada`.
JSON-функции должны быть доступны в сборке.
Другие функции:

- Для строк: LENGTH/LOWER/UPPER/TRIM/REPLACE.
- Для чисел: ABS/RANDOM.
- Для агрегации: COUNT/SUM/AVG/MIN/MAX.
- Для условий и NULL: CASE/COALESCE/NULLIF/IFNULL.
- Для даты и времени: DATE/TIME/DATETIME/STRFTIME.

`'now'` без localtime даёт UTC.
Проверьте преобразования времени и неоднозначные сдвиги месяцев на своих данных.

Формы SQL для уже созданной схемы — справка, не последовательность миграции:

```text
PRAGMA table_info(users);
PRAGMA index_list(users);
PRAGMA index_info(posts_user_created_idx);
SELECT name, sql FROM sqlite_schema WHERE type = 'index';
EXPLAIN QUERY PLAN SELECT * FROM posts WHERE user_id = 1;
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users RENAME COLUMN phone TO phone_number;
ALTER TABLE users DROP COLUMN phone_number;
```

PK/UNIQUE уже обеспечивают нужную уникальность.
Не создавайте вторую копию того же индекса без причины.
Планировщик использует составной или частичный индекс из полного примера, только если индекс выгоден плану.
DROP COLUMN появился в 3.35.0 и имеет ограничения на зависимости.
Не считайте ALTER TABLE универсальным.
После фиксации DROP TABLE удаляет таблицу вместе с данными.
DELETE без WHERE очищает все строки.
Вместо необязательного DELETE LIMIT можно выбрать id подзапросом:
`WHERE id IN (SELECT id FROM users WHERE ... ORDER BY id LIMIT 10)`.


## Транзакция в приложении

**Средний уровень.** В полном примере выбран autocommit=True.
Методы db.commit()/rollback() не управляют показанной SQL-транзакцией.
Транзакцией управляют SQL COMMIT/ROLLBACK.
При autocommit=False Python поддерживает постоянно открытую транзакцию.
В этом режиме методы имеют другое поведение.
Не смешивайте режимы неявно.
Контекст `with db:` не закрывает соединение и не создаёт вложенный SAVEPOINT.
Для вложенного отката задайте явный SAVEPOINT.
`executescript` имеет особенности фиксации в legacy-режиме.

Для нескольких связанных изменений начните транзакцию через BEGIN.
Выполните все команды.
При успехе выполните COMMIT.
При исключении выполните ROLLBACK.
Затем повторно передайте исключение через `raise`.
BEGIN IMMEDIATE запрашивает право записи в начале.
Если writer уже есть, возможно ожидание или SQLITE_BUSY.
Режим EXCLUSIVE ведёт себя по-разному в rollback-journal и WAL.
EXCLUSIVE не является универсальным средством ускорения.


## CLI и другие языки

**Базовый уровень.** Следующие команды выполняются в оболочке.
`sqlite3 database.db` открывает или создаёт файл.
`sqlite3 -readonly existing.db` открывает существующий файл только для чтения.
`sqlite3 -bail database.db < script.sql` исполняет скрипт с остановкой при ошибке.
Внутри CLI вводите следующие команды по одной.
Пояснения вынесены из строк команд:

```text
.help
.tables
.schema users
.headers on
.mode column
.output results.txt
.output
.quit
```

.output перенаправляет результаты в файл.
Без аргумента .output возвращает stdout.
Для CSV задайте `.mode csv`.
Затем выполните `.import file.csv table_name` с учётом заголовков и существующей схемы.
У dot-команд нет синтаксиса inline-комментариев.
Не передавайте dot-команды в Connection.execute.

В других языках подключение требует подходящего драйвера и закрытия ресурса:

- [Node.js node:sqlite](https://nodejs.org/api/sqlite.html) — встроенный API соответствующей версии Node.
  Пакет npm sqlite3 предоставляет другой API. Не смешивайте эти API.
- [Xerial SQLite JDBC](https://github.com/xerial/sqlite-jdbc) — драйвер для `jdbc:sqlite:...`. Одного DriverManager без драйвера недостаточно.
- [Microsoft.Data.Sqlite](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/) — откройте SqliteConnection. Освободите соединение через using.

Версия SQLite в этих драйверах может отличаться от Python и CLI.


## Источники

- [Python sqlite3 / transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [функции](https://www.sqlite.org/lang_corefunc.html), [даты](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [индексы](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
- [SQLite 3.53.4: release notes](https://www.sqlite.org/releaselog/3_53_4.html).
