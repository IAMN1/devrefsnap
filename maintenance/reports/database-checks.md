# История проверок материалов по базам данных

Записи перенесены из читательских страниц.
Даты, результаты и ограничения ниже описывают выполненную работу на момент записи.
Они не подтверждают состояние текущего окружения читателя.

## databases/README.md

Исходная страница: [databases/README.md](../../databases/README.md).

Прежняя таблица статусов:

| Тема | Содержание | Статус |
| --- | --- | --- |
| [SQL](../../databases/sql/README.md) | Общие запросы и явно обозначенные различия диалектов | Актуализировано |
| [PostgreSQL](../../databases/relational/postgresql/README.md) | Запросы, эксплуатация и [проверка резервной копии](../../databases/relational/postgresql/backup-and-restore.md) | Актуализировано |
| [SQLite](../../databases/relational/sqlite/README.md) | Встраиваемая СУБД, [копия и восстановление](../../databases/relational/sqlite/backup-and-restore.md), миграции | Актуализировано |
| [Redis](../../databases/non-relational/redis/README.md) | Структуры данных, TTL, кэш и обмен сообщениями | Добавлено |

Паспорта указывают диалекты, версии, выполненные сценарии и непроверенные серверные операции.

## databases/non-relational/redis/README.md

Исходная страница: [databases/non-relational/redis/README.md](../../databases/non-relational/redis/README.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06; Redis command reference и руководства; в источниках выбрана ветка 8.2, где доступен переключатель |
| Выполнено | 2026-11-06: Redis 8.2.11 / redis-py 8.1.0 / Python 3.14.7; все 3 Python-сценария на отдельном Unix socket, TCP/persistence отключены, только синтетические ключи |
| Не проверено | Сохранность на диске/restore, Sentinel/Cluster, аварии и нагрузка; учебный shell-запуск сверён по синтаксису |

Redis Open Source 8.2, GA / Extended по официальной таблице поддержки; это не утверждение «последняя версия»

- Предметные официальные источники и границы проверки приведены на подробных страницах.

## databases/non-relational/redis/data-and-caching.md

Исходная страница: [databases/non-relational/redis/data-and-caching.md](../../databases/non-relational/redis/data-and-caching.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: полный пример на Redis 8.2.11 / redis-py 8.1.0 / Python 3.14.7, выделенный Unix socket; проверены структуры, INCR, KEEPTTL и истечение; ключи очищены |
| Не проверено | Прикладная cache-aside интеграция, нагрузка, eviction и отказы сервера |

## databases/non-relational/redis/operations.md

Исходная страница: [databases/non-relational/redis/operations.md](../../databases/non-relational/redis/operations.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06 |
| Выполнено | Эксплуатационные сценарии, persistence, failover и Cluster не выполнялись |

## databases/non-relational/redis/transactions-and-messaging.md

Исходная страница: [databases/non-relational/redis/transactions-and-messaging.md](../../databases/non-relational/redis/transactions-and-messaging.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: оба полных сценария на Redis 8.2.11 / redis-py 8.1.0 / Python 3.14.7; проверены WATCH-отказ, runtime error без rollback, pending/ACK и Pub/Sub; свой Unix socket и ключи |
| Не проверено | Cluster, failover, падение consumer с внешним побочным эффектом и повторная доставка при авариях |

## databases/relational/postgresql/README.md

Исходная страница: [databases/relational/postgresql/README.md](../../databases/relational/postgresql/README.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06, PostgreSQL 18; доступны release notes 18.6 |
| Выполнено | 2026-11-06: все 12 SQL-блоков README, queries и schema-and-indexes в PostgreSQL 18.6 / PGlite 0.5.15, в памяти, WebAssembly; прошли пять групп проверок результатов |
| Backup/restore выполнено | 2026-11-06: нативные PostgreSQL, pg_dump, pg_restore и psql 18.6 в отдельном контейнере; custom/plain и ожидаемые отказы. [Сценарий](../../databases/relational/postgresql/backup-lab.md) |
| Не проверено | Конкурентные блокировки, производительность, прочие административные операции, перенос рабочих прав и PITR |

PostgreSQL 18; синтаксис сверяется с документацией этой ветки

Это основное место темы и пилот актуализации.
Паспорт относится к этому каталогу.
Предыдущую редакцию можно найти в истории Git.
PostgreSQL 19 RC не используется как стабильная цель.

- Проверенные предметные ссылки приведены также на каждой подробной странице.

## databases/relational/postgresql/backup-and-restore.md

Исходная страница: [databases/relational/postgresql/backup-and-restore.md](../../databases/relational/postgresql/backup-and-restore.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06: PostgreSQL 18, release notes 18.6 |
| Выполнено | 2026-11-06: PostgreSQL, pg_dump, pg_restore и psql 18.6; Linux arm64 в одноразовом контейнере; [полный сценарий](../../databases/relational/postgresql/backup-lab.md) |
| Не проверено | Production-права и владельцы, перенос между major-версиями, параллельный restore, PITR, аварийное восстановление и производительность |

В этой теме успешно запускались сервер и клиенты одной версии: 18.6.

Параллельные режимы здесь сверены только с документацией.

Пример не проверяет перенос прав рабочей БД.

## databases/relational/postgresql/backup-lab.md

Исходная страница: [databases/relational/postgresql/backup-lab.md](../../databases/relational/postgresql/backup-lab.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06: PostgreSQL 18, release notes 18.6 |
| Выполнено | 2026-11-06: сервер и клиенты 18.6, Debian arm64, Bash 5.2.37; одноразовый контейнер без внешней сети и опубликованных портов |

В тестовом запуске использовалась версия 18.6.

Проверка восстановления прав не входит в этот сценарий.

Сценарий не проверяет RLS, расширения, большие объёмы, конкурентные DDL и права рабочих ролей.

При проверке материалов весь одноразовый контейнер был удалён после завершения проверки.

## databases/relational/postgresql/operations.md

Исходная страница: [databases/relational/postgresql/operations.md](../../databases/relational/postgresql/operations.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | Не выполнялось; сервер, службы и расширения не настраивались |

## databases/relational/postgresql/queries.md

Исходная страница: [databases/relational/postgresql/queries.md](../../databases/relational/postgresql/queries.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | 2026-11-06, PostgreSQL 18.6 / PGlite 0.5.15, в памяти, WebAssembly: все SQL-блоки страницы; проверены JOIN/суммы, данные после отката, оконные результаты |
| Подготовка дополнительно выполнена | 2026-11-06: createdb, psql и полный queries.sql на нативном PostgreSQL 18.6 в [учебном сценарии копии](../../databases/relational/postgresql/backup-lab.md) |
| Не проверено | Остальные SQL-фрагменты на нативном сервере; конкурентные сеансы |

## databases/relational/postgresql/schema-and-indexes.md

Исходная страница: [databases/relational/postgresql/schema-and-indexes.md](../../databases/relational/postgresql/schema-and-indexes.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | 2026-11-06, PostgreSQL 18.6 / PGlite 0.5.15, в памяти, WebAssembly: все SQL-блоки страницы; проверены JSONB/FTS, четыре индекса, откат партиций и materialized view |
| Не проверено | Нативный сервер, конкурентное построение индексов, блокировки и производительность; полученный учебный план не является измерением рабочей нагрузки |

## databases/relational/sqlite/README.md

Исходная страница: [databases/relational/sqlite/README.md](../../databases/relational/sqlite/README.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06; текущие SQLite docs и Python 3.14; SQLite docs не фиксированы по major |
| Выполнено | 2026-11-06: Python 3.14.7 / SQLite 3.53.4; полные Python-примеры запросов, миграции и backup/restore; отдельный SQL-фрагмент функций; отказы ограничений и rollback |
| Backup CLI выполнено | 2026-11-06: sqlite3 3.54.0, macOS, Bash 3.2.57; бинарная и SQL-копия, восстановление и проверки. [Сценарий](../../databases/relational/sqlite/backup-lab.md#проверить-cli-копию-и-sql-dump) |
| Не проверено | Прочие CLI-рецепты, другие драйверы, конкурирующие записи во время backup, конкурентный WAL и аварийное восстановление |

Python 3.14 sqlite3; SQLite 3.53.4 в Python, 3.54.0 в CLI-проверке копий. STRICT/RETURNING требуют SQLite 3.37+ / 3.35+

## databases/relational/sqlite/backup-and-migrations.md

Исходная страница: [databases/relational/sqlite/backup-and-migrations.md](../../databases/relational/sqlite/backup-and-migrations.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06: Python 3.14, SQLite docs и release notes 3.53.4 |
| Выполнено | 2026-11-06: Python 3.14.7 / SQLite 3.53.4; полный сценарий в своём временном каталоге; сохранение FK, индекса и триггера, отказ нового CHECK |
| Не проверено | Конкурентный WAL, сбои питания и миграция произвольной пользовательской схемы |

## databases/relational/sqlite/backup-and-restore.md

Исходная страница: [databases/relational/sqlite/backup-and-restore.md](../../databases/relational/sqlite/backup-and-restore.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06: Python 3.14, текущие SQLite docs; release notes SQLite 3.53.4 и 3.54.0 |
| Выполнено через Python | 2026-11-06: Python 3.14.7 / SQLite 3.53.4, macOS; копия открытой WAL-БД, восстановление и отказы; [полный сценарий](../../databases/relational/sqlite/backup-lab.md#проверить-backup-api) |
| Выполнено через CLI | 2026-11-06: sqlite3 3.54.0, macOS, Bash 3.2.57; `.backup`, `.restore`, `.dump`, восстановление SQL и проверки; [полный сценарий](../../databases/relational/sqlite/backup-lab.md#проверить-cli-копию-и-sql-dump) |
| Не проверено | Конкурирующие записи во время backup, сбои питания, VACUUM INTO, шифрованные БД, внешние файлы и другие драйверы |

Запись о `VACUUM INTO`:

> Отдельная альтернатива с ограничениями; здесь не выполнялась

Проверка не доказывает поведение при произвольной конкурентной нагрузке и сбоях питания.

Запись о `VACUUM INTO`:

> Сама операция здесь не выполнялась.

## databases/relational/sqlite/backup-lab.md

Исходная страница: [databases/relational/sqlite/backup-lab.md](../../databases/relational/sqlite/backup-lab.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06: Python 3.14, SQLite docs, release notes 3.53.4 и 3.54.0 |
| Выполнено через Python | 2026-11-06: Python 3.14.7 / SQLite 3.53.4, macOS |
| Выполнено через CLI | 2026-11-06: sqlite3 3.54.0, macOS, Bash 3.2.57 |
| Не проверено | Конкурирующие writer, сбои питания, шифрование и произвольная схема с расширениями |

## databases/relational/sqlite/python-and-queries.md

Исходная страница: [databases/relational/sqlite/python-and-queries.md](../../databases/relational/sqlite/python-and-queries.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: Python 3.14.7 / SQLite 3.53.4; полный пример и SQL-функции; проверены FK/STRICT отказ, JOIN, RETURNING, cascade и rollback |
| Не проверено | CLI, Node/JDBC/.NET и несколько конкурентных соединений |

Эти драйверы здесь не запускались. Их версия SQLite может отличаться от Python и CLI.

## databases/sql/README.md

Исходная страница: [databases/sql/README.md](../../databases/sql/README.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06; PostgreSQL 18, MySQL 8.4, SQL Server, SQLite |
| Выполнено | 2026-11-06: все 6 SQL-блоков справочника/queries, 11 точных результатов на SQLite 3.53.4 (Python 3.14.7) и PostgreSQL 18.6 / PGlite 0.5.15 (в памяти, WebAssembly) |
| Не проверено | MySQL/SQL Server, нативный PostgreSQL CLI, конкурентность и производительность |

## databases/sql/dialects-and-transactions.md

Исходная страница: [databases/sql/dialects-and-transactions.md](../../databases/sql/dialects-and-transactions.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 / MySQL 8.4 / SQL Server 17.x / SQLite |
| Выполнено | Таблицы ниже — справочные формы, не единый исполняемый сценарий; MySQL/SQL Server не запускались |

Oracle здесь не запускался.

## databases/sql/queries.md

Исходная страница: [databases/sql/queries.md](../../databases/sql/queries.md).

| Запись | Историческое значение |
| --- | --- |
| Сверено с документацией | 2026-11-06 |
| Выполнено | 2026-11-06: все 5 SQL-блоков страницы, точные результаты и сохранение данных после отката на SQLite 3.53.4 / Python 3.14.7 и PostgreSQL 18.6 / PGlite 0.5.15 (WebAssembly, в памяти) |
| Не проверено | Показанные команды CLI, MySQL/SQL Server и конкурентные сеансы |
