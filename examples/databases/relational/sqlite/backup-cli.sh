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
