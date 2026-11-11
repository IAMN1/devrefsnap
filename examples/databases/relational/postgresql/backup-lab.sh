#!/usr/bin/env bash
set -euo pipefail
umask 077
export LC_ALL=C
backup_dir=$(mktemp -d "${TMPDIR:-/tmp}/pg-backup-lab.XXXXXX")

snapshot() {
    psql --host=127.0.0.1 --username=postgres --dbname="$1" \
      --no-psqlrc --set=ON_ERROR_STOP=1 --tuples-only --no-align --command="SELECT jsonb_build_object(
        'users', (SELECT jsonb_agg(u ORDER BY id) FROM demo.users AS u),
        'products', (SELECT jsonb_agg(p ORDER BY id) FROM demo.products AS p),
        'orders', (SELECT jsonb_agg(o ORDER BY id) FROM demo.orders AS o));"
}

createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_demo
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --no-psqlrc --set=ON_ERROR_STOP=1 --file=queries.sql
before=$(snapshot cheatsheet_demo)

pg_dump --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --format=custom --file="$backup_dir/cheatsheet_demo.dump"
pg_restore --list "$backup_dir/cheatsheet_demo.dump" > "$backup_dir/contents.txt"
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_restore_check
pg_restore --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_check \
  --single-transaction --exit-on-error --no-owner --no-privileges \
  "$backup_dir/cheatsheet_demo.dump"
test "$(snapshot cheatsheet_restore_check)" = "$before"
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_check \
  --no-psqlrc --set=ON_ERROR_STOP=1 --file=verify-backup.sql

# Занятое имя должно остановить цепочку до восстановления.
if createdb --host=127.0.0.1 --username=postgres cheatsheet_restore_check \
     2> "$backup_dir/existing.log" && touch "$backup_dir/guard-failed"; then
    printf 'ERROR: existing database was accepted\n' >&2
    exit 1
fi
grep -q 'already exists' "$backup_dir/existing.log"
test ! -e "$backup_dir/guard-failed"
test "$(snapshot cheatsheet_restore_check)" = "$before"

pg_dump --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --format=plain --no-owner --no-privileges --file="$backup_dir/backup.sql"
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_plain_check
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_plain_check \
  --no-psqlrc --set=ON_ERROR_STOP=1 --single-transaction --file="$backup_dir/backup.sql"
test "$(snapshot cheatsheet_plain_check)" = "$before"
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_plain_check \
  --no-psqlrc --set=ON_ERROR_STOP=1 --file=verify-backup.sql

createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_restore_error
pg_restore --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_error \
  --schema-only --single-transaction --no-owner --no-privileges "$backup_dir/cheatsheet_demo.dump"
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_error \
  --no-psqlrc --set=ON_ERROR_STOP=1 \
  --command="ALTER TABLE demo.orders ADD CONSTRAINT reject_order_amount CHECK (amount < 10);"
if pg_restore --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_error \
     --data-only --single-transaction --exit-on-error --no-owner --no-privileges \
     "$backup_dir/cheatsheet_demo.dump" 2> "$backup_dir/rejected.log"; then
    printf 'ERROR: incompatible CHECK accepted the restore\n' >&2
    exit 1
fi
grep -q 'reject_order_amount' "$backup_dir/rejected.log"
remaining=$(psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_restore_error \
  --no-psqlrc --set=ON_ERROR_STOP=1 --tuples-only --no-align --command="SELECT
    (SELECT count(*) FROM demo.users) + (SELECT count(*) FROM demo.products) +
    (SELECT count(*) FROM demo.orders);")
test "$remaining" = 0
test "$(snapshot cheatsheet_demo)" = "$before"
printf 'PostgreSQL backup/restore OK\nАрхивы: %s\n' "$backup_dir"
