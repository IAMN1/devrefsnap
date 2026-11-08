# Проверить перестроение таблицы SQLite

Откройте страницу, если изменение схемы требует создания и замены таблицы.
Пример сохраняет известные индекс, триггер и внешний ключ в синтетической БД.
[К карточкам миграции и WAL](backup-and-migrations.md) · [К SQLite](README.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Добавить CHECK через перестроение известной схемы | Копирование и замена в одной транзакции | [Код и запуск](#полный-пример-перестроение-таблицы) |

| Параметр | Значение |
| --- | --- |
| Уровень | Продвинутый |
| Предпосылки | Python 3.14 со SQLite 3.37+; FK и SQL-транзакции |
| Границы | Известная схема users/posts/audit; не универсальный перенос views и triggers |

## Полный пример: перестроение таблицы

Сохраните пример как `migration.py`.
Выполните `python3.14 migration.py`.
Зависимости входят в стандартную библиотеку Python.
Скрипт создаёт и затем удаляет только собственный временный каталог с синтетической БД.
Перед изменением своей схемы получите [проверенную резервную копию](backup-and-restore.md#проверить-восстановленную-бд).

Пример перестраивает известную таблицу и заменяет её в одной транзакции.
Пример не переносит произвольную схему с неизвестными views/triggers автоматически.
Удаление таблицы ниже касается только созданной учебной БД.

<!-- example: sqlite/migration.py -->
```python
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix="sqlite-migration-") as directory:
    folder = Path(directory)
    with closing(sqlite3.connect(folder / "source.db", autocommit=True)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        db.executescript("""
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT NOT NULL) STRICT;
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL
            ) STRICT;
            CREATE TABLE audit (username TEXT NOT NULL) STRICT;
            CREATE INDEX users_username_idx ON users(username);
            CREATE TRIGGER users_audit AFTER UPDATE ON users
            BEGIN INSERT INTO audit VALUES (NEW.username); END;
            INSERT INTO users VALUES (1, 'alice');
            INSERT INTO posts VALUES (1, 1, 'SQLite');
        """)
        # Переключение FK выполняется вне транзакции, иначе PRAGMA не подействует.
        db.execute("PRAGMA foreign_keys = OFF")
        assert db.execute("PRAGMA foreign_keys").fetchone() == (0,)
        try:
            db.execute("BEGIN IMMEDIATE")
            dependent_sql = db.execute("""
                SELECT sql FROM sqlite_schema
                WHERE tbl_name = 'users' AND type IN ('index', 'trigger') AND sql IS NOT NULL
                ORDER BY type, name
            """).fetchall()
            db.execute("""CREATE TABLE users_new (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL CHECK (username <> '')
            ) STRICT""")
            db.execute("INSERT INTO users_new (id, username) SELECT id, username FROM users")
            db.execute("DROP TABLE users")
            db.execute("ALTER TABLE users_new RENAME TO users")
            for (sql,) in dependent_sql:
                db.execute(sql)
            assert db.execute("PRAGMA foreign_key_check").fetchall() == []
            db.execute("COMMIT")
        except BaseException:
            if db.in_transaction:
                db.execute("ROLLBACK")
            raise
        finally:
            db.execute("PRAGMA foreign_keys = ON")

        assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
        db.execute("UPDATE users SET username = ? WHERE id = ?", ("alice-updated", 1))
        assert db.execute("SELECT username FROM audit").fetchall() == [("alice-updated",)]
        assert db.execute("SELECT user_id FROM posts").fetchall() == [(1,)]
        assert "users_username_idx" in {row[1] for row in db.execute("PRAGMA index_list(users)")}
        try:
            db.execute("UPDATE users SET username = '' WHERE id = 1")
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Новый CHECK должен запретить пустое имя")
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        print("SQLite", sqlite3.sqlite_version)
        print("OK: FK, index/trigger preservation, migration CHECK")
```

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
