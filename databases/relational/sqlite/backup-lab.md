# Проверить копию SQLite в учебном окружении

Повторите backup/restore без изменения рабочей БД.
Выберите Python API или CLI.
Каждый сценарий создаёт и удаляет только свой временный каталог с синтетическими данными.
[Карточки backup/restore](backup-and-restore.md) · [Миграция схемы](backup-and-migrations.md).

| Задача | Сценарий | Проверки |
| --- | --- | --- |
| Проверить копию открытой WAL-БД | [Python API](#проверить-backup-api) | Снимок, схема, ограничения, триггер и отказы |
| Проверить бинарную и SQL-копию | [CLI](#проверить-cli-копию-и-sql-dump) | `.backup`, `.restore`, `.dump`, integrity/FK и поведение |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; ограничения WAL и отказы — продвинутый |
| Предпосылки | Python 3.14 со sqlite3 либо Bash и sqlite3 CLI; схема STRICT требует SQLite 3.37 |
| Сверено с документацией | 2026-11-06: Python 3.14, SQLite docs, release notes 3.53.4 и 3.54.0 |
| Выполнено через Python | 2026-11-06: Python 3.14.7 / SQLite 3.53.4, macOS |
| Выполнено через CLI | 2026-11-06: sqlite3 3.54.0, macOS, Bash 3.2.57 |
| Не проверено | Конкурирующие writer, сбои питания, шифрование и произвольная схема с расширениями |

## Проверить backup API

Сохраните полный пример как `backup.py`.
Запустите `python3.14 backup.py`.
Зависимости входят в стандартную библиотеку Python.

Источник остаётся открытым в WAL; конкурирующего writer здесь нет.
После создания копии сценарий меняет источник.
Восстановленная БД должна содержать прежний снимок.
Целевые файлы резервируются через `touch(exist_ok=False)` и не заменяют существующие файлы.
При ошибке backup созданная цель может остаться неполной; сценарий удалит её вместе со своим каталогом.

<!-- example: sqlite/backup.py -->
```python
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory


def copy_to_new(source_path: Path, target_path: Path) -> None:
    source_uri = source_path.resolve().as_uri() + "?mode=ro"
    with closing(sqlite3.connect(source_uri, uri=True, autocommit=True)) as source:
        target_path.touch(exist_ok=False)
        with closing(sqlite3.connect(target_path, autocommit=True)) as target:
            source.backup(target)


def verify_restored(db: sqlite3.Connection) -> None:
    db.execute("PRAGMA foreign_keys = ON")
    assert db.execute("PRAGMA foreign_keys").fetchone() == (1,)
    assert db.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []
    assert db.execute("SELECT id, username FROM users").fetchall() == [(1, "alice")]
    assert db.execute("SELECT id, user_id, title FROM posts").fetchall() == [(1, 1, "SQLite")]
    objects = dict(db.execute("SELECT name, type FROM sqlite_schema WHERE sql IS NOT NULL"))
    assert objects["users_username_idx"] == "index"
    assert objects["users_audit"] == "trigger"
    db.execute("BEGIN")
    try:
        db.execute("UPDATE users SET username = 'alice-check' WHERE id = 1")
        assert db.execute("SELECT username FROM audit").fetchall() == [("alice-check",)]
    finally:
        db.execute("ROLLBACK")
    assert db.execute("SELECT username FROM users").fetchall() == [("alice",)]
    assert db.execute("SELECT username FROM audit").fetchall() == []
    for sql in (
        "INSERT INTO posts VALUES (2, 999, 'invalid reference')",
        "UPDATE users SET username = '' WHERE id = 1",
    ):
        try:
            db.execute(sql)
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("Restored constraint must reject invalid data")
    assert db.execute("PRAGMA foreign_key_check").fetchall() == []


with TemporaryDirectory(prefix="sqlite-backup-") as directory:
    folder = Path(directory)
    source_path = folder / "source.db"
    backup_path = folder / "backup.db"
    restored_path = folder / "restored.db"
    with closing(sqlite3.connect(source_path, autocommit=True)) as source:
        assert source.execute("PRAGMA journal_mode = WAL").fetchone() == ("wal",)
        source.execute("PRAGMA wal_autocheckpoint = 0")
        source.execute("PRAGMA foreign_keys = ON")
        source.executescript("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL CHECK (username <> '')
            ) STRICT;
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
        assert Path(str(source_path) + "-wal").stat().st_size > 0
        copy_to_new(source_path, backup_path)
        source.execute("UPDATE users SET username = 'alice-live' WHERE id = 1")
        copy_to_new(backup_path, restored_path)
        with closing(sqlite3.connect(restored_path, autocommit=True)) as restored:
            verify_restored(restored)
        assert source.execute("SELECT username FROM users").fetchall() == [("alice-live",)]
        assert source.execute("SELECT username FROM audit").fetchall() == [("alice-live",)]

    saved = backup_path.read_bytes()
    try:
        copy_to_new(source_path, backup_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Existing backup must not be replaced")
    assert backup_path.read_bytes() == saved

    missing = folder / "missing.db"
    missing_target = folder / "missing-target.db"
    try:
        copy_to_new(missing, missing_target)
    except sqlite3.OperationalError:
        pass
    else:
        raise AssertionError("Missing source must not become an empty backup")
    assert not missing.exists()
    assert not missing_target.exists()

    invalid = folder / "invalid.db"
    invalid.write_bytes(b"not a SQLite database")
    try:
        copy_to_new(invalid, folder / "invalid-target.db")
    except sqlite3.DatabaseError:
        pass
    else:
        raise AssertionError("Invalid source must not be accepted")
    print("Python backup/restore OK; SQLite", sqlite3.sqlite_version)
```

**Результат:** `Python backup/restore OK; SQLite ...`.
Копия сохраняет исходную `alice`; источник после копии содержит `alice-live`.
Проверка триггера откатывает свои изменения в восстановленной БД.
Занятое имя, отсутствующий источник и неверный формат файла вызывают ожидаемые отказы.
Это не сценарий восстановления уже повреждённой БД через recovery-инструменты.

## Проверить CLI-копию и SQL dump

Сохраните полный пример как `backup-cli.sh`.
Запустите `bash backup-cli.sh`.
Зависимости: Bash и sqlite3 CLI с поддержкой STRICT.
Скрипт сам создаёт исходную БД; внешние файлы и сервер не нужны.

`set -C` защищает новые целевые имена от перезаписи перенаправлением.
Команды `.backup` и `.restore` сами по себе могут заменить содержимое существующей цели.
Все пути ниже относятся только к созданному временному каталогу.

<!-- example: sqlite/backup-cli.sh -->
```bash
#!/usr/bin/env bash
set -euo pipefail
umask 077
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/sqlite-backup-cli.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
cd "$task_dir"

sqlite3 -init /dev/null -batch -bail source.db <<'SQL'
PRAGMA foreign_keys = ON;
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL CHECK (username <> '')
) STRICT;
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
SQL
before=$(cksum < source.db)

( set -C; : > backup.db ) && \
sqlite3 -init /dev/null -batch -bail -readonly source.db ".backup backup.db"
( set -C; : > restored.db ) && \
sqlite3 -init /dev/null -batch -bail restored.db ".restore backup.db"
( set -C; sqlite3 -init /dev/null -batch -bail -readonly source.db ".dump" > dump.sql ) && \
( set -C; : > restored-sql.db ) && \
sqlite3 -init /dev/null -batch -bail restored-sql.db < dump.sql

for target in restored.db restored-sql.db; do
    test "$(sqlite3 -init /dev/null -batch -bail "$target" 'PRAGMA integrity_check;')" = ok
    test -z "$(sqlite3 -init /dev/null -batch -bail "$target" 'PRAGMA foreign_key_check;')"
    test "$(sqlite3 -init /dev/null -batch -bail "$target" 'SELECT id, username FROM users;')" = '1|alice'
    test "$(sqlite3 -init /dev/null -batch -bail "$target" 'SELECT id, user_id, title FROM posts;')" = '1|1|SQLite'
    objects=$(sqlite3 -init /dev/null -batch -bail "$target" "SELECT count(*) FROM sqlite_schema
      WHERE (name = 'users_username_idx' AND type = 'index') OR (name = 'users_audit' AND type = 'trigger');")
    test "$objects" = 2
    audit=$(sqlite3 -init /dev/null -batch -bail "$target" "BEGIN;
      UPDATE users SET username = 'alice-check' WHERE id = 1;
      SELECT username FROM audit; ROLLBACK;")
    test "$audit" = alice-check
    if sqlite3 -init /dev/null -batch -bail "$target" \
         "PRAGMA foreign_keys=ON; INSERT INTO posts VALUES (2, 999, 'invalid');" 2> fk.log; then
        printf 'ERROR: foreign key accepted invalid data\n' >&2
        exit 1
    fi
    grep -q 'FOREIGN KEY constraint failed' fk.log
    if sqlite3 -init /dev/null -batch -bail "$target" \
         "UPDATE users SET username = '' WHERE id = 1;" 2> check.log; then
        printf 'ERROR: CHECK accepted empty username\n' >&2
        exit 1
    fi
    grep -q 'CHECK constraint failed' check.log
    test "$(sqlite3 -init /dev/null -batch -bail "$target" 'SELECT username FROM users;')" = alice
    test "$(sqlite3 -init /dev/null -batch -bail "$target" 'SELECT count(*) FROM audit;')" = 0
done

# Занятое имя останавливает команду до записи в готовую копию.
saved=$(cksum < backup.db)
if ( set -C; : > backup.db ) 2> existing.log && \
   sqlite3 -init /dev/null -batch -bail -readonly source.db ".backup backup.db"; then
    printf 'ERROR: existing backup was accepted\n' >&2
    exit 1
fi
test "$(cksum < backup.db)" = "$saved"
test "$(cksum < source.db)" = "$before"

# Успешный integrity_check не заменяет foreign_key_check.
sqlite3 -init /dev/null -batch -bail -readonly backup.db ".backup bad-fk.db"
sqlite3 -init /dev/null -batch -bail bad-fk.db \
  "PRAGMA foreign_keys=OFF; INSERT INTO posts VALUES (2, 999, 'invalid');"
test "$(sqlite3 -init /dev/null -batch -bail bad-fk.db 'PRAGMA integrity_check;')" = ok
test -n "$(sqlite3 -init /dev/null -batch -bail bad-fk.db 'PRAGMA foreign_key_check;')"
printf 'CLI backup/restore OK\n'
```

**Результат:** `CLI backup/restore OK`.
Обе восстановленные БД содержат ожидаемые строки, индекс и работающий триггер.
Проверки подтверждают отказ FK/CHECK и сохранность исходного файла.
Отдельная учебная БД показывает нарушение FK при успешном `integrity_check`.
Версия CLI проверяется отдельно: `sqlite3 --version`.

## Источники

- [Backup API](https://www.sqlite.org/backup.html), [Python Connection.backup](https://docs.python.org/3.14/library/sqlite3.html#sqlite3.Connection.backup), [CLI и dump](https://www.sqlite.org/cli.html).
- [Integrity check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign key check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check), [WAL](https://www.sqlite.org/wal.html).
- [Release notes 3.53.4](https://www.sqlite.org/releaselog/3_53_4.html), [release notes 3.54.0](https://www.sqlite.org/releaselog/3_54_0.html).
