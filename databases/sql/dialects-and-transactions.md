# Выбрать диалект и гарантии операции

[К SQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Средний — DDL/диалекты; продвинутый — изоляция/планы |
| Предпосылки | Общий SQL; для практики — отдельная учебная БД соответствующей СУБД |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 / MySQL 8.4 / SQL Server 17.x / SQLite |
| Выполнено | Таблицы ниже — справочные формы, не единый исполняемый сценарий; MySQL/SQL Server не запускались |

## Различия диалектов

В ячейках — формы синтаксиса с условными именами t, c, i; замените их и проверьте типы/ограничения.
Это не последовательность команд для копирования целиком.

| Задача | PostgreSQL 18 | MySQL 8.4 | SQL Server | SQLite |
| --- | --- | --- | --- | --- |
| Генерируемый ключ | `GENERATED ALWAYS AS IDENTITY` + PK | `AUTO_INCREMENT` + индекс | `IDENTITY(1,1)` + PK | `INTEGER PRIMARY KEY`; AUTOINCREMENT нужен лишь для особой политики повторного использования id |
| Первые строки | `ORDER BY id LIMIT 10` | `ORDER BY id LIMIT 10` | `TOP (10)` и ORDER BY | `ORDER BY id LIMIT 10` |
| Пропуск строк | `LIMIT 10 OFFSET 20` или OFFSET/FETCH | `LIMIT 10 OFFSET 20` | `ORDER BY id OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY` | `LIMIT 10 OFFSET 20` |
| Вернуть изменение | `RETURNING id` | Для AUTO_INCREMENT — LAST_INSERT_ID; общего DML RETURNING нет | `OUTPUT inserted.id` / `deleted.id`; положение в команде отличается | `RETURNING id` с 3.35.0; ограничения отличаются от PostgreSQL |
| Изменить тип | `ALTER TABLE t ALTER COLUMN c TYPE ...` | `ALTER TABLE t MODIFY COLUMN c ...` | `ALTER TABLE t ALTER COLUMN c ...` | Поддержка ALTER ограничена; сложные изменения — через перестроение таблицы |
| Удалить индекс | `DROP INDEX i` | `DROP INDEX i ON t` | `DROP INDEX i ON t` | `DROP INDEX i` |
| UPDATE из другой таблицы | `UPDATE ... SET ... FROM ...` | `UPDATE ... JOIN ... SET ...` | `UPDATE ... SET ... FROM ...` со своими правилами alias | UPDATE FROM с 3.33.0; не всякая форма PostgreSQL переносится |
| Частичный индекс | `CREATE INDEX ... WHERE ...` | Общего аналога с WHERE нет | Filtered index, ограничения на предикат | `CREATE INDEX ... WHERE ...` |
| Полнотекстовый поиск | tsvector + GIN/GiST | FULLTEXT + MATCH/AGAINST | FULLTEXT INDEX и соответствующий каталог/ключ | FTS5, если включён в сборку |

Для Oracle современный row limiting — FETCH FIRST/OFFSET FETCH; ROWNUM применяется со своим
порядком вычисления. Это отдельный диалект; Oracle здесь не запускался.
Сортировка NULL, кавычки идентификаторов, boolean, даты, функции строк и case sensitivity также различаются.

## Структура, индексы и план

**Средний уровень.** Общая схема SQL-конструкций, не исполняемый пример:

```text
CREATE TABLE t (id INTEGER PRIMARY KEY, value INTEGER NOT NULL CHECK (value >= 0));
ALTER TABLE t ADD COLUMN note ...;
ALTER TABLE t ADD CONSTRAINT ...;  -- поддержка/синтаксис зависят от СУБД
CREATE [UNIQUE] INDEX i ON t (value, id);
DROP TABLE t;                    -- удалит таблицу и данные после фиксации/автофиксации
```

NOT NULL, UNIQUE, PRIMARY KEY, FOREIGN KEY и CHECK защищают разные свойства.
CHECK со значением NULL не равнозначен запрету NULL. DROP TABLE CASCADE — не переносимая универсальная команда.
Добавление/удаление ограничения и перестроение таблицы могут блокировать работу: прежде нужен план миграции и проверенная копия.

**Продвинутый уровень.** Индекс расходует место и удорожает запись; выбирайте по реальным фильтрам,
JOIN и сортировкам. Порядок столбцов составного индекса важен. Планировщик использует статистику,
а наличие индекса не обязывает его выбирать. Частичный, функциональный и полнотекстовый индекс — разные задачи.

| СУБД | Посмотреть индексы / план |
| --- | --- |
| PostgreSQL | `pg_indexes`, psql `\d`; EXPLAIN, EXPLAIN ANALYZE |
| MySQL | SHOW INDEX FROM t; EXPLAIN / EXPLAIN ANALYZE |
| SQL Server | sys.indexes; estimated / actual execution plan; ALTER INDEX ... REBUILD — обслуживание, не анализ |
| SQLite | PRAGMA index_list(t), index_info(i); EXPLAIN QUERY PLAN |

Actual plan / EXPLAIN ANALYZE может выполнить запрос: не запускайте его на изменяющем SQL,
считая только объяснением. Сопоставляйте оценки с фактом, проверяйте индексы, статистику и объём результата.
Советы «всегда заменяйте JOIN подзапросом» или «всегда отключайте seq scan» не универсальны.

## Транзакции и изоляция

**Средний уровень.** Логика неделимой операции: начать → выполнить все части → проверить → COMMIT;
при ошибке — ROLLBACK всей операции. ROLLBACK TO SAVEPOINT отменяет только действия после точки.
SAVEPOINT после списания денег и откат зачисления с последующим COMMIT оставили бы списание без зачисления.

| СУБД | Начало / savepoint | Граница гарантии |
| --- | --- | --- |
| PostgreSQL | BEGIN; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Большинство DDL транзакционны; TRUNCATE откатывается, sequence не откатывается |
| MySQL InnoDB | START TRANSACTION; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Многие DDL и TRUNCATE вызывают implicit commit; движок таблицы имеет значение |
| SQL Server | BEGIN TRANSACTION; SAVE TRANSACTION s; ROLLBACK TRANSACTION s | Обработка ошибок/XACT_STATE и вложенных транзакций отличается от PostgreSQL |
| SQLite | BEGIN [DEFERRED/IMMEDIATE/EXCLUSIVE]; SAVEPOINT s; ROLLBACK TO s | Один writer; режим журнала и Python autocommit влияют на управление |

**Продвинутый уровень.** Названия изоляции описывают набор допустимых аномалий, но реализации отличаются.
В PostgreSQL READ UNCOMMITTED = READ COMMITTED, по умолчанию READ COMMITTED;
в MySQL InnoDB по умолчанию REPEATABLE READ. Настройки SQL Server READ COMMITTED/SNAPSHOT
и режимы SQLite нужно проверять в своём окружении. SERIALIZABLE не устраняет необходимость обработки ошибок:
при конфликте приложение может получить отказ и должно повторить всю транзакцию по определённой политике.

## Безопасность и сопровождаемость

Пользовательские значения передаются параметрами драйвера; имена таблиц/полей параметрами обычно
не подставляются, для них нужен отдельный контролируемый выбор. Роль приложения получает минимальные права.
Хеширование паролей пользователей приложения — задача подходящей password-hashing библиотеки,
а не простого SQL-хеша. Backup считается пригодным после проверенного восстановления.
Явные alias, единый стиль имён и короткие комментарии к причинам упрощают чтение сложного SQL.

## Источники

- [MySQL 8.4: ALTER TABLE](https://dev.mysql.com/doc/refman/8.4/en/alter-table.html), [CREATE TABLE](https://dev.mysql.com/doc/refman/8.4/en/create-table.html), [implicit commit](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html), [изоляция InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html).
- [SQL Server: DROP INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-index-transact-sql?view=sql-server-ver17), [ORDER BY / OFFSET](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql?view=sql-server-ver17), [OUTPUT](https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql?view=sql-server-ver17).
- [PostgreSQL: изоляция](https://www.postgresql.org/docs/18/transaction-iso.html), [TRUNCATE](https://www.postgresql.org/docs/18/sql-truncate.html).
- [SQLite: ALTER TABLE](https://www.sqlite.org/lang_altertable.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [AUTOINCREMENT](https://www.sqlite.org/autoinc.html).
