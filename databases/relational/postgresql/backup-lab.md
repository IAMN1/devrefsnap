# Проверить копию PostgreSQL в учебном окружении

Повторите полный цикл custom/plain и проверьте отказ восстановления.
Используйте отдельный сервер с синтетическими данными.
[Карточки backup/restore](backup-and-restore.md) · [Справочник PostgreSQL](README.md).

| Задача | Где выполнять | Пример |
| --- | --- | --- |
| Проверить данные и ограничения | `psql` восстановленной БД | [SQL проверки](#проверить-данные-и-ограничения) |
| Создать обе копии и восстановить их | Оболочка учебного сервера | [Полный сценарий](#проверить-custom-plain-и-отказ-восстановления) |
| Очистить учебные ресурсы | После просмотра результата | [Очистка](#очистить-учебные-ресурсы) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; проверка отката при отказе — продвинутый |
| Предпосылки | Bash, PostgreSQL 18, psql/pg_dump/pg_restore/createdb; отдельный сервер с ролью postgres |
| Сверено с документацией | 2026-11-06: PostgreSQL 18, release notes 18.6 |
| Выполнено | 2026-11-06: сервер и клиенты 18.6, Debian arm64, Bash 5.2.37; одноразовый контейнер без внешней сети и опубликованных портов |
| Границы | Синтетическая схема demo; custom/plain, равенство данных, ограничения, identity, занятое имя цели и откат data-only restore при ошибке CHECK |

## Подготовить входные файлы

Сохраните [полный учебный SQL](queries.md#полный-пример-учебная-база) как `queries.sql`.
Сохраните два блока ниже как `verify-backup.sql` и `backup-lab.sh` в той же папке.
Убедитесь, что сервер и клиенты относятся к PostgreSQL 18.
В тестовом запуске использовалась версия 18.6.
Сценарий подключается к `127.0.0.1` под `postgres`.
При другой установке задайте адрес и роль отдельно.
Не используйте рабочий сервер для этого сценария.

Сценарий создаёт четыре БД с фиксированными учебными именами.
Если любое создаваемое имя уже занято, `createdb` остановит сценарий.
Сценарий не удаляет существующие БД и не использует `--clean`.
Каталог копий создаётся через `mktemp`; сценарий выводит его путь.
Ресурсы остаются после выполнения для просмотра.

## Проверить данные и ограничения

Полный файл `verify-backup.sql` предназначен только для восстановленной учебной БД.
Проверки сравнивают данные с известным набором из `queries.sql`.
SQL также проверяет связь заказов, UNIQUE, CHECK и следующий identity.
Ошибочный результат вызывает исключение и останавливает `psql` с `ON_ERROR_STOP`.
Проверки завершаются rollback; значения последовательностей всё равно могут продвинуться.

<!-- example: postgresql/verify-backup.sql -->
```sql
BEGIN;
DO $check$
DECLARE
    next_user_id bigint;
BEGIN
    IF (SELECT count(*) FROM demo.users) <> 3
       OR (SELECT count(*) FROM demo.products) <> 3
       OR (SELECT count(*) FROM demo.orders) <> 3
       OR (SELECT stock FROM demo.products WHERE id = 1) IS DISTINCT FROM 10 THEN
        RAISE EXCEPTION 'Unexpected restored data';
    END IF;
    IF (SELECT sum(o.amount) FROM demo.orders AS o
        JOIN demo.users AS u ON u.id = o.user_id WHERE u.username = 'alice')
       IS DISTINCT FROM 140.00 THEN
        RAISE EXCEPTION 'Unexpected order total';
    END IF;

    INSERT INTO demo.users (username, email) VALUES ('restore-check', 'restore@example.test')
    RETURNING id INTO next_user_id;
    IF next_user_id <> 4 THEN
        RAISE EXCEPTION 'Identity sequence was not restored';
    END IF;

    BEGIN
        INSERT INTO demo.orders (user_id, product_id, amount, status, ordered_at)
        VALUES (999, 1, 1, 'paid', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Foreign key did not reject the order';
    EXCEPTION WHEN foreign_key_violation THEN
        NULL;
    END;
    BEGIN
        UPDATE demo.products SET stock = -1 WHERE id = 1;
        RAISE EXCEPTION 'CHECK did not reject negative stock';
    EXCEPTION WHEN check_violation THEN
        NULL;
    END;
    BEGIN
        INSERT INTO demo.users (username, email) VALUES ('alice', 'duplicate@example.test');
        RAISE EXCEPTION 'UNIQUE did not reject duplicate username';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;
END
$check$;
ROLLBACK;
```

**Результат:** `DO` и `ROLLBACK` без ошибки.
Повторная проверка identity на той же БД потребует нового восстановления: последовательность уже могла продвинуться.
Для рабочей БД нужны собственные инварианты и проверки приложения.

## Проверить custom, plain и отказ восстановления

Полный Bash-скрипт использует три подготовленных файла из одной папки.
Запустите `bash backup-lab.sh` из этой папки.
Архив и SQL-файл доверенные: сценарий сам создаёт их из учебной схемы.

`--no-owner --no-privileges` намеренно пропускают владельцев и ACL.
Проверка восстановления прав не входит в этот сценарий.
Data-only restore ниже намеренно запускается в несовместимую синтетическую схему для проверки отката.
Для обычного восстановления используйте новую пустую БД по [карточке restore](backup-and-restore.md#логическая-копия-и-восстановление-в-новую-бд).

<!-- example: postgresql/backup-lab.sh -->
```bash
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
```

**Результат:** `PostgreSQL backup/restore OK`.
Обе восстановленные БД содержат исходный набор данных.
Ошибка CHECK не оставляет ранее загруженные строки в `cheatsheet_restore_error`.
Сравнение подтверждает сохранность данных исходной `cheatsheet_demo`.
Сценарий не проверяет RLS, расширения, большие объёмы, конкурентные DDL и права рабочих ролей.

## Очистить учебные ресурсы

Сначала просмотрите восстановленные БД и сохраните нужные архивы.
Следующий фрагмент **удаляет четыре учебные БД целиком**.
Проверьте сервер и каждое имя перед запуском:

```bash
dropdb --host=127.0.0.1 --username=postgres cheatsheet_restore_check
dropdb --host=127.0.0.1 --username=postgres cheatsheet_plain_check
dropdb --host=127.0.0.1 --username=postgres cheatsheet_restore_error
dropdb --host=127.0.0.1 --username=postgres cheatsheet_demo
```

Каталог архивов удаляется отдельно после сохранения нужной копии.
При проверке материалов весь одноразовый контейнер был удалён после завершения проверки.

## Источники

- [pg_dump](https://www.postgresql.org/docs/18/app-pgdump.html), [pg_restore](https://www.postgresql.org/docs/18/app-pgrestore.html), [psql](https://www.postgresql.org/docs/18/app-psql.html).
- [Identity](https://www.postgresql.org/docs/18/ddl-identity-columns.html), [ограничения](https://www.postgresql.org/docs/18/ddl-constraints.html), [release notes 18.6](https://www.postgresql.org/docs/18/release-18-6.html).
