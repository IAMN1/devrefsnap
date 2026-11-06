# Подключение, схема и запросы SQLite

[К SQLite](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — подключение/CRUD; средний — ограничения/индексы/транзакции |
| Предпосылки | Python 3.14 со штатным sqlite3; SQLite 3.37+ для STRICT |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: Python 3.14.7 / SQLite 3.53.4; полный пример и SQL-функции; проверены FK/STRICT отказ, JOIN, RETURNING, cascade и rollback |
| Не проверено | CLI, Node/JDBC/.NET и несколько конкурентных соединений |

## Полный пример: блог в памяти

Сохраните блок как `demo.py`.
Выполните `python3.14 demo.py`.
Зависимостей из pip нет.
База живёт только в памяти данного соединения.
Пример не открывает пользовательские файлы.
Параметр autocommit=True выбран явно.
SQL-команды BEGIN/COMMIT/ROLLBACK ниже управляют транзакцией.

<!-- example: sqlite/demo.py -->
```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect(":memory:", autocommit=True)) as db:
    db.execute("PRAGMA foreign_keys = ON")
    assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
    db.executescript("""
        BEGIN;
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            age INTEGER CHECK (age >= 0),
            is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) STRICT;
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        ) STRICT;
        CREATE TABLE comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            body TEXT NOT NULL
        ) STRICT;
        CREATE INDEX posts_user_created_idx ON posts(user_id, created_at);
        CREATE INDEX users_active_idx ON users(username) WHERE is_active = 1;
        COMMIT;
    """)
    db.executemany(
        "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
        [("alice", "alice@example.test", 30),
         ("bob", "bob@example.test", 25),
         ("carol", "carol@example.test", None)],
    )
    db.executemany("INSERT INTO posts (user_id, title) VALUES (?, ?)",
                   [(1, "SQLite"), (2, "SQL")])
    db.execute("INSERT INTO comments (post_id, user_id, body) VALUES (?, ?, ?)",
               (1, 2, "Useful"))

    rows = db.execute("""
        SELECT u.username, COUNT(p.id)
        FROM users AS u LEFT JOIN posts AS p ON p.user_id = u.id
        GROUP BY u.id, u.username ORDER BY u.username
    """).fetchall()
    assert rows == [("alice", 1), ("bob", 1), ("carol", 0)]

    for sql, params in [
        ("INSERT INTO posts (user_id, title) VALUES (?, ?)", (999, "Invalid")),
        ("INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
         ("bad", "bad@example.test", "not-an-integer")),
    ]:
        try:
            db.execute(sql, params)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Ожидался отказ ограничения")

    db.execute("BEGIN IMMEDIATE")
    try:
        user_id = db.execute(
            "INSERT INTO users (username, email) VALUES (?, ?) RETURNING id",
            ("dave", "dave@example.test"),
        ).fetchone()[0]
        assert user_id == 4
        db.execute("UPDATE users SET age = ? WHERE username = ?", (31, "alice"))
        db.execute("DELETE FROM users WHERE id = ?", (2,))
        assert db.execute("SELECT COUNT(*) FROM comments").fetchone() == (0,)
    finally:
        db.execute("ROLLBACK")
    assert db.execute("SELECT age FROM users WHERE id = 1").fetchone() == (30,)
    assert db.execute("SELECT COUNT(*) FROM users").fetchone() == (3,)
    assert db.execute("SELECT COUNT(*) FROM comments").fetchone() == (1,)
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    print("SQLite", sqlite3.sqlite_version)
    print("OK: JOIN, parameters, FK/STRICT refusal, RETURNING, cascade and rollback")
```

Пример проверяет успешный JOIN.
Пример проверяет отказ для неизвестного пользователя и неверного типа.
Пример также проверяет каскадное удаление и полный откат удаления.
Прочитайте результат RETURNING до фиксации.
`last_insert_rowid()` / cursor.lastrowid относятся к последней соответствующей вставке в соединении.
RETURNING часто яснее связывает id с конкретной командой.

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

Эти драйверы здесь не запускались. Их версия SQLite может отличаться от Python и CLI.

## Источники

- [Python sqlite3 / transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control), [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).
- [STRICT](https://www.sqlite.org/stricttables.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [функции](https://www.sqlite.org/lang_corefunc.html), [даты](https://www.sqlite.org/lang_datefunc.html).
- [CLI](https://www.sqlite.org/cli.html), [индексы](https://www.sqlite.org/lang_createindex.html), [ALTER TABLE](https://www.sqlite.org/lang_altertable.html).
