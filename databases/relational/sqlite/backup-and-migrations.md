# Резервная копия, миграция и конкуренция SQLite

[К SQLite](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Средний — backup/restore; продвинутый — перестроение схемы/WAL |
| Предпосылки | Python 3.14 со SQLite 3.37+; понимание FK/транзакций |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: Python 3.14.7 / SQLite 3.53.4; полный сценарий в своём временном каталоге, backup/restore, integrity/FK, сохранение индекса/триггера, отказ нового CHECK |
| Не проверено | CLI dump/restore, конкурентный WAL, сбои питания и миграция произвольной пользовательской схемы |

## Полный пример: копия, восстановление и миграция

Сохраните пример как `backup-migration.py`.
Выполните `python3.14 backup-migration.py`.
Скрипт создаёт и затем удаляет **только собственный временный каталог** с синтетической БД.
Скрипт получает согласованную копию через backup API.
Затем скрипт восстанавливает копию в новый файл и перестраивает известную таблицу.
Скрипт не переносит произвольную схему с неизвестными views/triggers автоматически.

<!-- example: sqlite/backup-migration.py -->
```python
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory(prefix="sqlite-cheatsheet-") as directory:
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
        with closing(sqlite3.connect(folder / "backup.db", autocommit=True)) as backup:
            db.backup(backup)
            with closing(sqlite3.connect(folder / "restored.db", autocommit=True)) as restored:
                backup.backup(restored)
                assert restored.execute("SELECT username FROM users").fetchall() == [("alice",)]
                assert restored.execute("PRAGMA integrity_check").fetchall() == [("ok",)]

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
        print("OK: backup/restore, integrity, FK, index/trigger preservation, migration CHECK")
```

Восстановленная БД содержит исходную alice.
Мигрированная БД содержит alice-updated и работающий аудит.
Скрипт проверяет сохранение внешней ссылки, индекса и триггера.
Скрипт также проверяет отказ нового CHECK.
Для произвольной схемы дополнительно сохраните и скорректируйте views, triggers и другие зависимости.
Следуйте официальной [процедуре перестроения](https://www.sqlite.org/lang_altertable.html#making_other_kinds_of_table_schema_changes).
Включите копирование данных и замену таблицы в одну транзакцию.

## CLI-копии и границы восстановления

**Средний уровень.** Команды предназначены для вашей учебной БД.
Заранее выберите пути к новым файлам:

```text
sqlite3 source.db ".backup backup.db"
sqlite3 source.db ".dump" > dump.sql
sqlite3 -bail restored.db < dump.sql
```

Выполняйте команды в оболочке.
.backup внутри кавычек — команда CLI.
`?DB?` в справке `.backup ?DB? FILE` означает необязательное имя БД, а не «показать прогресс».
Для наблюдения за прогрессом в Python у backup есть callback progress.
Проверьте резервное копирование и восстановление на отдельной цели.
Существующий файл назначения может быть перезаписан или изменён.
Используйте новый путь вне рабочей БД.
SQL dump содержит исполняемый код.
Не восстанавливайте недоверенный файл без проверки.
`VACUUM INTO` — ещё один штатный путь создания компактной копии со своими ограничениями.

## Конкуренция и WAL

**Продвинутый уровень.** SQLite допускает много readers и одного writer.
BEGIN IMMEDIATE получает право записи заранее.
При конкуренции BEGIN IMMEDIATE может завершиться SQLITE_BUSY.
Держите транзакции короткими.
Не выполняйте сетевые ожидания внутри транзакций.
Timeout/busy handler задают ожидание.
Ожидание не отменяет ограничение одного writer.

WAL обычно позволяет читателям работать параллельно с writer.
WAL требует совместимой файловой системы и процесса checkpoint.
Общая БД на сетевой файловой системе — не универсальный сценарий WAL.
Долгое чтение может задерживать checkpoint и увеличивать WAL.
Следите за временем транзакций и размером файлов.
Настройка synchronous влияет на гарантии при сбоях и производительность.
Выбирайте режим по требованиям к данным.

`PRAGMA journal_mode=WAL` меняет режим файла.
Эта настройка не является обязательной строкой каждого подключения.
Активный `-wal` содержит существенные данные.
Не удаляйте активный `-wal` вручную.
Не копируйте только основной файл активной БД.
Получайте согласованную копию через backup API или штатные команды.
`PRAGMA integrity_check` проверяет структуру.
`PRAGMA foreign_key_check` проверяет ссылки.
Эти проверки не заменяют друг друга.

## Источники

- [SQLite backup API](https://www.sqlite.org/backup.html), [Python Connection.backup](https://docs.python.org/3.14/library/sqlite3.html#sqlite3.Connection.backup), [VACUUM INTO](https://www.sqlite.org/lang_vacuum.html#vacuuminto).
- [Изменение схемы](https://www.sqlite.org/lang_altertable.html), [транзакции](https://www.sqlite.org/lang_transaction.html), [foreign_keys](https://www.sqlite.org/pragma.html#pragma_foreign_keys).
- [WAL](https://www.sqlite.org/wal.html), [integrity_check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign_key_check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check).
