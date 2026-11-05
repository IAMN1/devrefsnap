# Подключение, права и эксплуатация

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — подключение; средний — права; продвинутый — конкуренция/мониторинг |
| Предпосылки | PostgreSQL 18; для demo-запросов — [учебная схема](queries.md#полный-пример-учебная-база); административные права оговариваются отдельно |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | Не выполнялось; сервер, службы и расширения не настраивались |

## Навигация

- [Установка и управление БД](#установка-и-управление-бд)
- [Подключение и команды psql](#подключение-и-команды-psql)
- [Роли и доступ](#роли-и-доступ)
- [Транзакции, изоляция и блокировки](#транзакции-изоляция-и-блокировки)
- [Мониторинг и обслуживание](#мониторинг-и-обслуживание)
- [Расширения и диагностика](#расширения-и-диагностика)
- [Источники](#источники)

## Установка и управление БД

**Базовый уровень.** Способ установки зависит от ОС и репозитория пакетов.
Используйте [официальный выбор платформы](https://www.postgresql.org/download/): пакет
`postgresql-18` не гарантирован стандартным репозиторием любого выпуска Ubuntu/Debian.
Служба systemd применяется только при соответствующей установке Linux; имя службы/кластера уточняют у пакета.

Для контейнера используйте [документацию официального образа](https://hub.docker.com/_/postgres):
она определяет переменные инициализации и путь тома для выбранного major.
При переходе с 16 на 18 недостаточно заменить тег образа: проверьте layout данных и процедуру обновления.
Не публикуйте учебный порт на все интерфейсы без необходимости; для локального доступа достаточно привязки к loopback.

Формы SQL ниже — справка, а не сценарий удаления учебной БД. Выполняются ролью с нужными правами;
CREATE/DROP DATABASE нельзя помещать в обычный блок транзакции.

```text
CREATE DATABASE database_name OWNER owner_role TEMPLATE template0 ENCODING 'UTF8';
ALTER DATABASE database_name RENAME TO new_name;
ALTER DATABASE database_name OWNER TO new_owner;
CREATE DATABASE copy_name TEMPLATE source_name;  -- источник не должен использоваться другими сеансами
DROP DATABASE database_name;  -- удалит БД целиком; сначала проверьте имя и резервную копию
```

Locale/провайдер сортировки должны существовать в окружении; значение вроде `en_US.UTF-8`
не переносимо автоматически между ОС. Копирование через TEMPLATE — не замена регулярному backup.

## Подключение и команды psql

**Базовый уровень.** Команда оболочки для уже созданной БД:

```bash
psql --host=127.0.0.1 --port=5432 --username=postgres \
  --dbname=cheatsheet_demo --no-psqlrc --set=ON_ERROR_STOP=1
```

Пароль не помещается в URL/командную строку. Для повторных подключений можно настроить
[password file](https://www.postgresql.org/docs/18/libpq-pgpass.html) с соответствующими правами файла.
Приложению нужна отдельная роль; postgres здесь используется только для изолированного учебного окружения.

SQL в соединении с БД:

```sql
SELECT current_database(), current_user;
SHOW server_version;
SELECT pg_size_pretty(pg_database_size(current_database()));
```

Ожидаемая БД — `cheatsheet_demo`; версия должна принадлежать ветке 18.
Размер зависит от окружения и не является фиксированным результатом примера.

Команды **внутри psql**, не SQL и не команды системной оболочки:

```text
\conninfo
\l
\dn
\dt demo.*
\d demo.users
\di demo.*
\du
\dp demo.*
\dx
\timing on
\x auto
\q
```

`\di` фильтрует имена индексов; индексы конкретной таблицы показывает `\d demo.users`.
Дополнительно: `\c` сменяет БД, `\df` показывает функции, `\dv` — представления,
`\i file.sql` читает файл, `\o file.txt` перенаправляет результат, `\?` и `\h SELECT` открывают справку.

## Роли и доступ

**Средний уровень.** Одноразовый фрагмент SQL в `cheatsheet_demo` для владельца demo-объектов,
который также имеет CREATEROLE (в учебном кластере это может быть postgres).
Создаёт постоянную роль и меняет права; повторный CREATE ROLE с тем же именем даст ошибку.

```sql
CREATE ROLE cheatsheet_reader NOLOGIN;
GRANT CONNECT ON DATABASE cheatsheet_demo TO cheatsheet_reader;
GRANT USAGE ON SCHEMA demo TO cheatsheet_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA demo TO cheatsheet_reader;

ALTER DEFAULT PRIVILEGES IN SCHEMA demo
GRANT SELECT ON TABLES TO cheatsheet_reader;

SELECT has_table_privilege('cheatsheet_reader', 'demo.users', 'SELECT') AS can_read,
       has_table_privilege('cheatsheet_reader', 'demo.users', 'INSERT') AS can_insert;
```

Ожидаются `can_read = t`, `can_insert = f` в исходном учебном окружении без дополнительных grants.
Default privileges относятся к будущим объектам **роли, исполнившей ALTER DEFAULT PRIVILEGES**;
для другого владельца требуется отдельная настройка FOR ROLE. ALL TABLES затрагивает уже существующие объекты.
USAGE на схему не заменяет SELECT на таблицу; права на БД не дают автоматически права на её содержимое.

Для отдельного входа создайте роль с LOGIN и выдайте ей членство в cheatsheet_reader;
пароль задавайте командой psql `\password role_name`, а не литералом в публикуемом скрипте.
Обратная операция выдаче — REVOKE; DROP ROLE потребует предварительно разобрать её владение и зависимости.

**Аутентификация:** предпочтителен `scram-sha-256`, MD5-пароли устаревают.
Изменения pg_hba.conf зависят от адресов, роли и TLS; строка `host all all 0.0.0.0/0 ...`
не является универсальной безопасной настройкой. Правила проверяются по порядку, первое совпавшее применяется.
`SHOW ssl` показывает настройку сервера; шифрование текущего соединения можно проверить так:

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

Результат зависит от способа подключения. Для удалённого TLS-клиента отдельно настраивают
проверку сертификата/имени сервера, например libpq `sslmode=verify-full`.

## Транзакции, изоляция и блокировки

**Продвинутый уровень.** Фрагмент SQL в demo-БД: удерживает блокировку строки до ROLLBACK;
не оставляйте такую транзакцию открытой в общем окружении.

```sql
BEGIN;
SELECT id, stock FROM demo.products WHERE id = 1 FOR UPDATE;
UPDATE demo.products SET stock = stock - 1 WHERE id = 1 AND stock > 0
RETURNING stock;
ROLLBACK;
```

Ожидается stock `10` при чтении и `9` в RETURNING; после отката — снова `10`.
Другое соединение, изменяющее ту же строку, может ждать освобождения блокировки.
FOR SHARE и FOR KEY SHARE решают другие задачи; LOCK TABLE выбирает режим блокировки всей таблицы.
В autocommit блокировка отдельного SELECT освобождается при завершении его транзакции.

| Изоляция PostgreSQL | Что учитывать |
| --- | --- |
| READ UNCOMMITTED | Работает как READ COMMITTED; грязных чтений нет |
| READ COMMITTED, по умолчанию | Новый снимок на каждую команду; повторный SELECT может увидеть другой результат |
| REPEATABLE READ | Снимок на транзакцию; в PostgreSQL предотвращает также phantom reads; возможен конфликт обновления |
| SERIALIZABLE | Проверка совместимости с последовательным выполнением; возможна ошибка сериализации |

Уровень задают в BEGIN или до первой команды чтения/записи через SET TRANSACTION.
При SQLSTATE `40001` приложение повторяет **всю** транзакцию с начала, а не только последнюю команду.
При deadlock (`40P01`) также нужен определённый приложением порядок действий/повтор.
Изменения sequence не откатываются вместе с данными: пропуски id нормальны.

ROLLBACK TO SAVEPOINT отменяет только действия после точки. Для неделимой бизнес-операции нельзя
откатить только вторую половину и зафиксировать первую; используйте полный ROLLBACK при неуспехе.

## Мониторинг и обслуживание

**Продвинутый уровень.** Диагностические фрагменты SQL в demo-БД:

```sql
SELECT pid, state, now() - query_start AS duration,
       wait_event_type, wait_event, query
FROM pg_stat_activity
WHERE datname = current_database()
  AND pid <> pg_backend_pid()
  AND state = 'active'
ORDER BY query_start;

SELECT schemaname, relname,
       pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
       n_live_tup, n_dead_tup
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

SELECT pid, pg_blocking_pids(pid) AS blocked_by
FROM pg_stat_activity
WHERE datname = current_database();
```

Ожидаются реальные сеансы и размеры, фиксированного числа строк нет.
Обычная роль видит часть сведений других сеансов; для мониторинга могут потребоваться специальные роли.
Отдельно проверяйте `idle in transaction`: такие сеансы способны удерживать блокировки и мешать очистке.
`pg_stat_user_indexes` показывает статистику использования индексов, `pg_statio_user_tables` — ввод/вывод,
`pg_locks` — блокировки. Отсутствие обращений в коротком интервале ещё не доказывает ненужность индекса.

Команды SQL ниже выполняются по отдельности, владельцем/ролью с нужными правами:

```sql
ANALYZE demo.orders;
VACUUM (ANALYZE) demo.orders;
```

Они обновляют статистику и обслуживают таблицу; VACUUM нельзя выполнять внутри явного блока транзакции.
Обычный VACUUM освобождает место для повторного использования внутри таблицы;
VACUUM FULL переписывает таблицу и берёт ACCESS EXCLUSIVE — это отдельная операция с запасом места и окном работ.
Autovacuum обычно нужно сохранять включённым и настраивать по измеряемой нагрузке.

`CHECKPOINT` принудительно записывает контрольную точку WAL, а не проверяет целостность.
Для физической проверки существуют [pg_amcheck](https://www.postgresql.org/docs/18/app-pgamcheck.html)
и проверка checksums офлайн; они требуют своих предпосылок и не заменяют проверку восстановления.
REINDEX тоже создаёт нагрузку/блокировки; варианты CONCURRENTLY рассмотрены в [индексах](schema-and-indexes.md#индексы-и-план-запроса).

## Расширения и диагностика

**Продвинутый уровень.** SQL-фрагмент для просмотра доступных и установленных расширений:

```sql
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('pg_trgm', 'unaccent', 'pgcrypto', 'uuid-ossp', 'pg_stat_statements')
ORDER BY name;
SELECT extname, extversion FROM pg_extension ORDER BY extname;
```

Набор строк зависит от пакетов сервера. CREATE EXTENSION подключает уже доступное расширение
к конкретной БД, но не скачивает системные пакеты. Права и доступность проверяют до установки.

| Задача | Возможность / граница |
| --- | --- |
| Похожие строки | [pg_trgm](https://www.postgresql.org/docs/18/pgtrgm.html): `similarity`, операторы и классы индексов |
| Нормализация диакритики | [unaccent](https://www.postgresql.org/docs/18/unaccent.html) |
| Криптографические функции | [pgcrypto](https://www.postgresql.org/docs/18/pgcrypto.html); не универсальная схема защиты данных приложения |
| UUID по дополнительным алгоритмам | [uuid-ossp](https://www.postgresql.org/docs/18/uuid-ossp.html); для встроенной `gen_random_uuid()` не нужно |
| Агрегированная статистика запросов | [pg_stat_statements](https://www.postgresql.org/docs/18/pgstatstatements.html): настройка shared_preload_libraries, перезапуск, затем CREATE EXTENSION в БД |
| Геоданные | [PostGIS](https://postgis.net/documentation/) — сторонний пакет и собственная матрица совместимости |
| Управление партициями | [pg_partman](https://github.com/pgpartman/pg_partman) — отдельная установка и регламент |
| Логическая репликация / переупаковка / отладка | Сторонние pglogical, pg_repack, pldbgapi: версии и ограничения сверяют с документацией проектов |
| Сжатие | Выбор хранения/TOAST и сторонних расширений зависит от задачи; команда `CREATE EXTENSION zstd` не гарантирована стандартной установкой |

Не перезаписывайте список shared_preload_libraries без учёта уже загруженных библиотек.
Сброс статистики уничтожает накопленные измерения; его согласуют с наблюдением.
Включение `log_statement = 'all'` может записать чувствительные значения и увеличить нагрузку;
для медленных запросов выбирают обоснованный порог `log_min_duration_statement`.
`RAISE NOTICE/EXCEPTION` используются внутри PL/pgSQL, а не как самостоятельный SQL-запрос.
Файлы postgresql.conf, pg_hba.conf и pg_ident.conf имеют разные назначения;
postgresql.auto.conf управляется ALTER SYSTEM.

## Источники

- [psql](https://www.postgresql.org/docs/18/app-psql.html), [CREATE DATABASE](https://www.postgresql.org/docs/18/sql-createdatabase.html), [схемы](https://www.postgresql.org/docs/18/ddl-schemas.html).
- [Права](https://www.postgresql.org/docs/18/ddl-priv.html), [default privileges](https://www.postgresql.org/docs/18/sql-alterdefaultprivileges.html), [SCRAM/MD5](https://www.postgresql.org/docs/18/auth-password.html), [pg_hba.conf](https://www.postgresql.org/docs/18/auth-pg-hba-conf.html).
- [Изоляция](https://www.postgresql.org/docs/18/transaction-iso.html), [блокировки](https://www.postgresql.org/docs/18/explicit-locking.html), [повтор сериализации](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html).
- [Статистика](https://www.postgresql.org/docs/18/monitoring-stats.html), [VACUUM](https://www.postgresql.org/docs/18/sql-vacuum.html), [CHECKPOINT](https://www.postgresql.org/docs/18/sql-checkpoint.html).
