# Выбрать диалект и гарантии операции

[К SQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Средний — DDL/диалекты; продвинутый — изоляция/планы |
| Предпосылки | Общий SQL; для практики — отдельная учебная БД соответствующей СУБД |

## Различия диалектов

Ячейки содержат формы синтаксиса с условными именами t, c, i.
Замените условные имена.
Проверьте типы и ограничения.
Таблица не задаёт последовательность команд для копирования целиком.

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

В Oracle современное ограничение числа строк задают через FETCH FIRST/OFFSET FETCH.
Для ROWNUM действует собственный порядок вычисления.
Oracle использует отдельный диалект.
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
Добавление или удаление ограничения и перестроение таблицы могут блокировать работу.
Перед изменением подготовьте план миграции.
Проверьте резервную копию.

**Продвинутый уровень.** Индекс расходует место и удорожает запись.
Выбирайте индекс по реальным фильтрам, JOIN и сортировкам.
Порядок столбцов составного индекса важен.
Планировщик использует статистику.
Наличие индекса не обязывает планировщик выбирать индекс.
Частичный, функциональный и полнотекстовый индексы решают разные задачи.

| СУБД | Посмотреть индексы / план |
| --- | --- |
| PostgreSQL | `pg_indexes`, psql `\d`; EXPLAIN, EXPLAIN ANALYZE |
| MySQL | SHOW INDEX FROM t; EXPLAIN / EXPLAIN ANALYZE |
| SQL Server | sys.indexes; estimated / actual execution plan; ALTER INDEX ... REBUILD — обслуживание, не анализ |
| SQLite | PRAGMA index_list(t), index_info(i); EXPLAIN QUERY PLAN |

Actual plan / EXPLAIN ANALYZE может выполнить запрос.
Не считайте такую проверку изменяющего SQL только объяснением.
Сопоставляйте оценки с фактическими значениями.
Проверьте индексы.
Проверьте статистику.
Оцените объём результата.
Советы «всегда заменяйте JOIN подзапросом» или «всегда отключайте seq scan» не универсальны.

## Транзакции и изоляция

**Средний уровень.** Начните транзакцию.
Выполните все части неделимой операции.
Проверьте результат.
При успехе выполните COMMIT.
При ошибке выполните ROLLBACK всей операции.
ROLLBACK TO SAVEPOINT отменяет только действия после точки.
Если SAVEPOINT стоит после списания денег, откат зачисления с последующим COMMIT оставит списание без зачисления.

| СУБД | Начало / savepoint | Граница гарантии |
| --- | --- | --- |
| PostgreSQL | BEGIN; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Большинство DDL транзакционны; TRUNCATE откатывается, sequence не откатывается |
| MySQL InnoDB | START TRANSACTION; SAVEPOINT s; ROLLBACK TO SAVEPOINT s | Многие DDL и TRUNCATE вызывают implicit commit; движок таблицы имеет значение |
| SQL Server | BEGIN TRANSACTION; SAVE TRANSACTION s; ROLLBACK TRANSACTION s | Обработка ошибок/XACT_STATE и вложенных транзакций отличается от PostgreSQL |
| SQLite | BEGIN [DEFERRED/IMMEDIATE/EXCLUSIVE]; SAVEPOINT s; ROLLBACK TO s | Один writer; режим журнала и Python autocommit влияют на управление |

**Продвинутый уровень.** Названия изоляции описывают набор допустимых аномалий, но реализации отличаются.
В PostgreSQL READ UNCOMMITTED работает как READ COMMITTED.
В PostgreSQL по умолчанию действует READ COMMITTED.
В MySQL InnoDB по умолчанию действует REPEATABLE READ.
Проверьте настройки SQL Server READ COMMITTED/SNAPSHOT и режимы SQLite в своём окружении.
SERIALIZABLE не устраняет необходимость обработки ошибок.
При конфликте приложение может получить отказ.
В этом случае приложение должно повторить всю транзакцию по определённой политике.

## Безопасность и сопровождаемость

Передавайте пользовательские значения параметрами драйвера.
Имена таблиц и полей обычно нельзя подставлять параметрами.
Для имён задайте отдельный контролируемый выбор.
Выдайте роли приложения минимальные права.
Для хеширования паролей пользователей приложения используйте подходящую password-hashing библиотеку.
Простой SQL-хеш не заменяет такую библиотеку.
Резервная копия считается пригодной после проверенного восстановления.
Явные alias, единый стиль имён и короткие комментарии к причинам упрощают чтение сложного SQL.

## Источники

- [MySQL 8.4: ALTER TABLE](https://dev.mysql.com/doc/refman/8.4/en/alter-table.html), [CREATE TABLE](https://dev.mysql.com/doc/refman/8.4/en/create-table.html), [implicit commit](https://dev.mysql.com/doc/refman/8.4/en/implicit-commit.html), [изоляция InnoDB](https://dev.mysql.com/doc/refman/8.4/en/innodb-transaction-isolation-levels.html).
- [SQL Server: DROP INDEX](https://learn.microsoft.com/en-us/sql/t-sql/statements/drop-index-transact-sql?view=sql-server-ver17), [ORDER BY / OFFSET](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-order-by-clause-transact-sql?view=sql-server-ver17), [OUTPUT](https://learn.microsoft.com/en-us/sql/t-sql/queries/output-clause-transact-sql?view=sql-server-ver17).
- [PostgreSQL: изоляция](https://www.postgresql.org/docs/18/transaction-iso.html), [TRUNCATE](https://www.postgresql.org/docs/18/sql-truncate.html).
- [SQLite: ALTER TABLE](https://www.sqlite.org/lang_altertable.html), [RETURNING](https://www.sqlite.org/lang_returning.html), [AUTOINCREMENT](https://www.sqlite.org/autoinc.html).
