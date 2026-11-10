# Подключение, права и эксплуатация

Откройте страницу для подключения, прав, конкуренции и диагностики PostgreSQL 18.
Изменяющие примеры предназначены для отдельного учебного сервера; административные права указаны рядом.

<a id="навигация"></a>

## Быстрый поиск

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Выбрать установку или создать БД | Пакет, контейнер и CREATE DATABASE | [Подготовка](#установка-и-управление-бд) |
| Проверить подключение и осмотреть объекты | psql, SHOW и метакоманды | [Подключение](#подключение-и-команды-psql) |
| Разрешить чтение существующих и будущих таблиц | GRANT и default privileges | [Права](#роли-и-доступ) |
| Защитить изменение общей строки | FOR UPDATE, изоляция и повтор | [Конкуренция](#транзакции-изоляция-и-блокировки) |
| Найти ожидание или обслужить таблицу | pg_stat_activity, блокировки, VACUUM | [Мониторинг](#мониторинг-и-обслуживание) |
| Проверить доступность расширения | pg_available_extensions и условия установки | [Расширения](#расширения-и-диагностика) |

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — подключение; средний — права; продвинутый — конкуренция/мониторинг |
| Предпосылки | PostgreSQL 18; для demo-запросов — [учебная схема](query-lab.md#полный-пример-учебная-база); административные права оговариваются отдельно |

## Установка и управление БД

**Базовый уровень.** Способ установки зависит от ОС и репозитория пакетов.
Используйте [официальный выбор платформы](https://www.postgresql.org/download/).
Стандартный репозиторий выпуска Ubuntu/Debian не обязательно содержит пакет `postgresql-18`.
Служба systemd применяется только при соответствующей установке Linux.
Уточните имя службы или кластера в документации пакета.

Для контейнера используйте [документацию официального образа](https://hub.docker.com/_/postgres).
Документация определяет переменные инициализации и путь тома для выбранного major.
При переходе с 16 на 18 недостаточно заменить тег образа.
Проверьте размещение данных и процедуру обновления.
Не публикуйте учебный порт на все интерфейсы без необходимости.
Для локального доступа достаточно привязки к loopback.

Формы SQL ниже служат справкой и не образуют сценарий удаления учебной БД.
Выполняйте команды ролью с нужными правами.
Не помещайте CREATE/DROP DATABASE в обычный блок транзакции.

```text
CREATE DATABASE database_name OWNER owner_role TEMPLATE template0 ENCODING 'UTF8';
ALTER DATABASE database_name RENAME TO new_name;
ALTER DATABASE database_name OWNER TO new_owner;
CREATE DATABASE copy_name TEMPLATE source_name;  -- источник не должен использоваться другими сеансами
DROP DATABASE database_name;  -- удалит БД целиком; сначала проверьте имя и резервную копию
```

Locale и провайдер сортировки должны существовать в окружении.
Значение вроде `en_US.UTF-8` не переносится автоматически между ОС.
Копирование через TEMPLATE не заменяет регулярное резервное копирование.

## Подключение и команды psql

**Базовый уровень.** Команда оболочки для уже созданной БД:

```bash
psql --host=127.0.0.1 --port=5432 --username=postgres \
  --dbname=cheatsheet_demo --no-psqlrc --set=ON_ERROR_STOP=1
```

Не помещайте пароль в URL или командную строку.
Для повторных подключений можно настроить [password file](https://www.postgresql.org/docs/18/libpq-pgpass.html) с соответствующими правами файла.
Выделите приложению отдельную роль.
Здесь postgres используется только для изолированного учебного окружения.

SQL в соединении с БД:

```sql
SELECT current_database(), current_user;
SHOW server_version;
SELECT pg_size_pretty(pg_database_size(current_database()));
```

Ожидаемая БД — `cheatsheet_demo`.
Версия должна принадлежать ветке 18.
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

`\di` фильтрует имена индексов.
Индексы конкретной таблицы показывает `\d demo.users`.
`\c` меняет БД.
`\df` показывает функции.
`\dv` показывает представления.
`\i file.sql` читает файл.
`\o file.txt` перенаправляет результат.
`\?` и `\h SELECT` открывают справку.

## Роли и доступ

Нужна роль чтения существующих и будущих demo-таблиц без права вставки.

**Средний уровень.** Выполните одноразовый фрагмент SQL в `cheatsheet_demo` от владельца demo-объектов с CREATEROLE.
В учебном кластере такой ролью может быть postgres.
Фрагмент создаёт постоянную роль и меняет права.
Повторный CREATE ROLE с тем же именем даст ошибку.

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
Default privileges относятся к будущим объектам **роли, исполнившей ALTER DEFAULT PRIVILEGES**.
Для другого владельца требуется отдельная настройка FOR ROLE.
ALL TABLES затрагивает уже существующие объекты.
USAGE на схему не заменяет SELECT на таблицу.
Права на БД не дают автоматически права на содержимое БД.

Для отдельного входа создайте роль с LOGIN.
Выдайте роли членство в cheatsheet_reader.
Задайте пароль командой psql `\password role_name`.
Не помещайте пароль литералом в публикуемый скрипт.
REVOKE отменяет выдачу прав.
Перед DROP ROLE разберите владение и зависимости роли.

**Аутентификация:** предпочтителен `scram-sha-256`.
MD5-пароли устаревают.
Изменения pg_hba.conf зависят от адресов, роли и TLS.
Строка `host all all 0.0.0.0/0 ...` не является универсальной безопасной настройкой.
Сервер проверяет правила по порядку и применяет первое совпавшее правило.
`SHOW ssl` показывает настройку сервера.
Проверьте шифрование текущего соединения следующим запросом:

```sql
SELECT ssl, version, cipher FROM pg_stat_ssl WHERE pid = pg_backend_pid();
```

Результат зависит от способа подключения.
Для удалённого TLS-клиента отдельно настройте проверку сертификата и имени сервера, например libpq `sslmode=verify-full`.

## Транзакции, изоляция и блокировки

Остаток товара меняют несколько соединений.
Чтение и изменение строки должны находиться в одной транзакции.

**Продвинутый уровень.** Фрагмент SQL в demo-БД удерживает блокировку строки до ROLLBACK.
Не оставляйте такую транзакцию открытой в общем окружении.

```sql
BEGIN;
SELECT id, stock FROM demo.products WHERE id = 1 FOR UPDATE;
UPDATE demo.products SET stock = stock - 1 WHERE id = 1 AND stock > 0
RETURNING stock;
ROLLBACK;
```

Ожидается stock `10` при чтении и `9` в RETURNING.
После отката stock снова равен `10`.
Другое соединение, изменяющее ту же строку, может ждать освобождения блокировки.
FOR SHARE и FOR KEY SHARE решают другие задачи.
LOCK TABLE выбирает режим блокировки всей таблицы.
В autocommit блокировка отдельного SELECT освобождается при завершении его транзакции.

| Изоляция PostgreSQL | Что учитывать |
| --- | --- |
| READ UNCOMMITTED | Работает как READ COMMITTED; грязных чтений нет |
| READ COMMITTED, по умолчанию | Новый снимок на каждую команду; повторный SELECT может увидеть другой результат |
| REPEATABLE READ | Снимок на транзакцию; в PostgreSQL предотвращает также phantom reads; возможен конфликт обновления |
| SERIALIZABLE | Проверка совместимости с последовательным выполнением; возможна ошибка сериализации |

Задайте уровень в BEGIN или через SET TRANSACTION до первой команды чтения или записи.
При SQLSTATE `40001` приложение повторяет **всю** транзакцию с начала, а не только последнюю команду.
При deadlock (`40P01`) также нужен определённый приложением порядок действий/повтор.
Изменения sequence не откатываются вместе с данными.
Пропуски id нормальны.

ROLLBACK TO SAVEPOINT отменяет только действия после точки.
Для неделимой бизнес-операции нельзя откатить только вторую половину и зафиксировать первую.
При неуспехе используйте полный ROLLBACK.

## Мониторинг и обслуживание

Запрос ждёт или таблица накапливает мёртвые строки.
Сначала найдите сеанс, блокировку и состояние таблицы.

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

Запросы возвращают реальные сеансы и размеры.
Фиксированного числа строк нет.
Обычная роль видит часть сведений других сеансов.
Для мониторинга могут потребоваться специальные роли.
Отдельно проверяйте `idle in transaction`.
Такие сеансы могут удерживать блокировки и мешать очистке.
`pg_stat_user_indexes` показывает статистику использования индексов.
`pg_statio_user_tables` показывает ввод и вывод.
`pg_locks` показывает блокировки.
Отсутствие обращений в коротком интервале ещё не доказывает ненужность индекса.

Выполняйте команды SQL ниже по отдельности от владельца или роли с нужными правами:

```sql
ANALYZE demo.orders;
VACUUM (ANALYZE) demo.orders;
```

Команды обновляют статистику и обслуживают таблицу.
Не выполняйте VACUUM внутри явного блока транзакции.
Обычный VACUUM освобождает место для повторного использования внутри таблицы.
VACUUM FULL переписывает таблицу и берёт ACCESS EXCLUSIVE.
Для VACUUM FULL предусмотрите запас места и окно работ.
Обычно сохраняйте autovacuum включённым.
Настраивайте autovacuum по измеряемой нагрузке.

`CHECKPOINT` принудительно записывает контрольную точку WAL без проверки целостности.
Для физической проверки существуют [pg_amcheck](https://www.postgresql.org/docs/18/app-pgamcheck.html) и проверка checksums офлайн.
У этих проверок есть собственные предпосылки.
Физические проверки не заменяют проверку восстановления.
REINDEX тоже создаёт нагрузку и блокировки.
Варианты CONCURRENTLY рассмотрены в [индексах](schema-and-indexes.md#индексы-и-план-запроса).

## Расширения и диагностика

Нужная возможность может требовать пакета сервера или перезапуска.
Сначала проверьте доступность и условия установки.

**Продвинутый уровень.** SQL-фрагмент для просмотра доступных и установленных расширений:

```sql
SELECT name, default_version, installed_version
FROM pg_available_extensions
WHERE name IN ('pg_trgm', 'unaccent', 'pgcrypto', 'uuid-ossp', 'pg_stat_statements')
ORDER BY name;
SELECT extname, extversion FROM pg_extension ORDER BY extname;
```

Набор строк зависит от пакетов сервера.
CREATE EXTENSION подключает уже доступное расширение к конкретной БД.
CREATE EXTENSION не скачивает системные пакеты.
До установки проверьте права и доступность расширения.

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
Сброс статистики уничтожает накопленные измерения.
Согласуйте сброс с процессом наблюдения.
Включение `log_statement = 'all'` может записать чувствительные значения и увеличить нагрузку.
Для медленных запросов выберите обоснованный порог `log_min_duration_statement`.
Используйте `RAISE NOTICE/EXCEPTION` внутри PL/pgSQL.
Эти конструкции не являются самостоятельным SQL-запросом.
Файлы postgresql.conf, pg_hba.conf и pg_ident.conf имеют разные назначения.
ALTER SYSTEM управляет postgresql.auto.conf.

## Источники

- [psql](https://www.postgresql.org/docs/18/app-psql.html), [CREATE DATABASE](https://www.postgresql.org/docs/18/sql-createdatabase.html), [схемы](https://www.postgresql.org/docs/18/ddl-schemas.html).
- [Права](https://www.postgresql.org/docs/18/ddl-priv.html), [default privileges](https://www.postgresql.org/docs/18/sql-alterdefaultprivileges.html), [SCRAM/MD5](https://www.postgresql.org/docs/18/auth-password.html), [pg_hba.conf](https://www.postgresql.org/docs/18/auth-pg-hba-conf.html).
- [Изоляция](https://www.postgresql.org/docs/18/transaction-iso.html), [блокировки](https://www.postgresql.org/docs/18/explicit-locking.html), [повтор сериализации](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html).
- [Статистика](https://www.postgresql.org/docs/18/monitoring-stats.html), [VACUUM](https://www.postgresql.org/docs/18/sql-vacuum.html), [CHECKPOINT](https://www.postgresql.org/docs/18/sql-checkpoint.html).
