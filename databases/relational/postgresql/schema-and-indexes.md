# Проектировать схему, индексы и поиск

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — типы/ограничения; средний — DDL/индексы; продвинутый — JSONB/FTS/партиции |
| Предпосылки | PostgreSQL 18; БД `cheatsheet_demo` и схема из [queries.sql](queries.md#полный-пример-учебная-база); подключение владельцем |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | 2026-11-06, PostgreSQL 18.6 / PGlite 0.5.15, в памяти, WebAssembly: все SQL-блоки страницы; проверены JSONB/FTS, четыре индекса, откат партиций и materialized view |
| Не проверено | Нативный сервер, конкурентное построение индексов, блокировки и производительность; полученный учебный план не является измерением рабочей нагрузки |

## Навигация

- [Типы и ограничения](#типы-и-ограничения)
- [Изменить таблицу и схему](#изменить-таблицу-и-схему)
- [Индексы и план запроса](#индексы-и-план-запроса)
- [JSONB и полнотекстовый поиск](#jsonb-и-полнотекстовый-поиск)
- [Партиционирование](#партиционирование)
- [Представления и подготовленные запросы](#представления-и-подготовленные-запросы)
- [Источники](#источники)

## Типы и ограничения

**Базовый уровень.** Основная схема уже показана в полном примере; это справочная таблица типов.

| Данные | Тип / конструкция | Существенное свойство |
| --- | --- | --- |
| Целые | `smallint`, `integer`, `bigint` | 2, 4, 8 байт; выбирайте по диапазону |
| Генерируемый ключ | `bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY` | identity генерирует значение, PRIMARY KEY обеспечивает уникальность и NOT NULL |
| Старые схемы | `serial`, `bigserial` | Сокращение для столбца с sequence; это не отдельные настоящие типы |
| Точные числа | `numeric(10, 2)` / `decimal(10, 2)` | Для точной десятичной арифметики; масштаб и точность ограничены объявлением |
| Приближённые числа | `real`, `double precision` | Не заменяют точную арифметику денежных величин |
| Текст / байты | `text`, `varchar(n)`, `char(n)`, `bytea` | `varchar(n)` ограничивает длину; `char(n)` дополняется пробелами |
| Логическое значение | `boolean` | true, false или NULL, если не задан NOT NULL |
| Момент времени | `timestamptz` | Хранится момент; вывод зависит от TimeZone, исходное имя зоны не сохраняется |
| Локальная дата/время | `date`, `time`, `timestamp`, `interval` | `timestamp` без time zone не определяет мировой момент |
| Структурированные данные | `json`, `jsonb`, `integer[]`, `text[]` | JSONB поддерживает собственные операторы и GIN; массивы не заменяют любые связи |
| Идентификаторы | `uuid` | `gen_random_uuid()` встроена; для неё не требуется uuid-ossp |
| Специальные задачи | enum, диапазоны, `inet`/`cidr`, геометрические типы | Подробности и допустимые операторы — в [каталоге типов](https://www.postgresql.org/docs/18/datatype.html) |

`CHECK (price >= 0)` сам по себе допускает NULL: при необходимости нужен ещё NOT NULL.
PRIMARY KEY/UNIQUE создают обеспечивающий уникальность индекс; дублировать его вручную не нужно.
Внешний ключ не создаёт автоматически индекс на ссылающемся столбце: необходимость оценивают по запросам и удалениям.
`ON DELETE CASCADE` удаляет связанные строки, а `RESTRICT` запрещает удаление используемой записи.

## Изменить таблицу и схему

**Средний уровень.** Фрагмент SQL в `cheatsheet_demo`; изменения учебной таблицы откатываются:

```sql
BEGIN;
ALTER TABLE demo.users ADD COLUMN phone text;
ALTER TABLE demo.products ALTER COLUMN price TYPE numeric(12, 2);
ALTER TABLE demo.products ADD CONSTRAINT products_name_nonempty CHECK (name <> '');
ALTER TABLE demo.users RENAME COLUMN phone TO phone_number;
ROLLBACK;
```

После отката столбца phone/phone_number нет, price остаётся numeric(10, 2).
ALTER TABLE может блокировать доступ и переписывать данные; возможность выполнить преобразование
безопасно на большой таблице проверяют отдельно. Удаление COLUMN/CONSTRAINT необратимо после фиксации
в смысле потери данных/защиты; CASCADE может удалить зависимые объекты.

Схема — пространство имён внутри БД. Имена `demo.users` надёжнее неявного search_path.
Общие формы DDL ниже — справка, не исполняемый набор:

```text
CREATE SCHEMA schema_name AUTHORIZATION owner_role;
ALTER TABLE schema_name.table_name SET SCHEMA other_schema;
ALTER TABLE schema_name.table_name OWNER TO other_owner;
ALTER TABLE schema_name.table_name ALTER COLUMN col SET DEFAULT expression;
DROP SCHEMA schema_name CASCADE;  -- удалит также содержимое и зависимости
```

## Индексы и план запроса

**Средний уровень.** Фрагмент SQL после queries.sql. Создаёт два учебных индекса один раз:

```sql
CREATE INDEX orders_user_date_idx ON demo.orders (user_id, ordered_at);
CREATE INDEX orders_pending_idx ON demo.orders (ordered_at) WHERE status = 'pending';

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, amount FROM demo.orders
WHERE user_id = 1 ORDER BY ordered_at;
```

Проверка: `psql`-команда `\d demo.orders` покажет индексы.
План зависит от статистики, объёма и настроек: на трёх строках последовательное чтение нормально.
EXPLAIN ANALYZE **выполняет** запрос; у изменяющего запроса будут реальные побочные эффекты.
Оптимизация начинается с плана и измерений, а не с общего запрета последовательного чтения.

| Метод / вариант | Когда рассматривать |
| --- | --- |
| B-tree, по умолчанию | Равенство, диапазоны и подходящие ORDER BY |
| hash | Равенство; польза относительно B-tree проверяется измерениями |
| GIN | JSONB, массивы, полнотекстовый поиск с подходящим классом операторов |
| GiST / SP-GiST | Специализированные операторы, геометрия, диапазоны и иные поддерживаемые структуры |
| BRIN | Большие таблицы с корреляцией значения с физическим порядком строк |
| Составной | Порядок столбцов и условия влияют на пользу; это не замена всем одиночным индексам |
| Частичный | Условие запроса должно позволять планировщику применить предикат индекса |
| По выражению | Например `lower(username)`; запрос должен использовать соответствующее выражение |
| `varchar_pattern_ops` / `text_pattern_ops` | Возможность ускорить префиксный LIKE зависит от типа, оператора и collation |

**Продвинутый уровень.** Общие формы ниже требуют заменить имена. CONCURRENTLY позволяет
не блокировать обычные записи на всё построение, но выполняется дольше, имеет ограничения и может ждать транзакции.
Это не синоним параллельного построения. Выполняется вне явного блока транзакции;
после ошибки проверяют, не остался ли невалидный индекс.

```text
CREATE INDEX CONCURRENTLY index_name ON schema_name.table_name (column_name);
REINDEX INDEX schema_name.index_name;
REINDEX INDEX CONCURRENTLY schema_name.index_name;
ALTER INDEX schema_name.index_name RENAME TO new_index_name;
DROP INDEX schema_name.index_name;  -- удалит индекс; проверьте зависимости и нагрузку
```

## JSONB и полнотекстовый поиск

**Продвинутый уровень.** Фрагменты SQL на demo-схеме. Первые запросы не меняют данные:

```sql
SELECT username, profile->>'city' AS city
FROM demo.users
WHERE profile @> '{"tags":["vip"]}'::jsonb;

SELECT username FROM demo.users WHERE profile ? 'city' ORDER BY username;

SELECT name FROM demo.products
WHERE to_tsvector('english', description) @@ plainto_tsquery('english', 'keyboard');
```

Ожидаются `alice | Moscow`; `alice`, `bob`; товар `Keyboard`.
`->` возвращает JSON/JSONB, `->>` — текст. Операторы `?`, `@>` и конкатенация `||` здесь
относятся к JSONB, их нельзя безоговорочно переносить на json.
Для обновления вложенного значения используют `jsonb_set`; сборку/агрегацию выполняют
`jsonb_build_object`, `jsonb_agg`, `jsonb_object_agg`.

Следующий фрагмент SQL создаёт постоянные учебные индексы один раз:

```sql
CREATE INDEX users_profile_gin ON demo.users USING GIN (profile);
CREATE INDEX products_fts_gin ON demo.products
USING GIN (to_tsvector('english', description));
```

Проверка — `\d demo.users` и `\d demo.products` в psql.
Для применения FTS-индекса выражение и конфигурация запроса должны соответствовать индексу.
В русских текстах нужна подходящая конфигурация, например `russian`; `english` выбран для данных примера.
Полнотекстовый поиск встроен: unaccent/pg_trgm решают дополнительные задачи, а не включают FTS.

## Партиционирование

**Продвинутый уровень.** Самостоятельный фрагмент SQL в `cheatsheet_demo`; создаёт новую таблицу в demo:

```sql
BEGIN;
CREATE TABLE demo.measurements (
    measured_on date NOT NULL,
    city_id integer NOT NULL,
    temperature numeric(5, 2),
    PRIMARY KEY (measured_on, city_id)
) PARTITION BY RANGE (measured_on);

CREATE TABLE demo.measurements_2026_11 PARTITION OF demo.measurements
FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

INSERT INTO demo.measurements VALUES ('2026-11-06', 1, 5.50);
SELECT tableoid::regclass AS partition, measured_on FROM demo.measurements;
ROLLBACK;
```

Ожидаются `demo.measurements_2026_11 | 2026-11-06`; после отката таблиц нет.
Начальная граница включена, конечная исключена. Строка вне существующих диапазонов
даст ошибку, если нет подходящей/default-партиции. Декларативное партиционирование и
наследование `INHERITS` — разные механизмы. Оно требует плана создания/удаления партиций
и не гарантирует ускорения любого запроса.

## Представления и подготовленные запросы

**Средний / продвинутый уровень.** Фрагмент SQL на demo-схеме; изменения схемы откатываются:

```sql
BEGIN;
CREATE MATERIALIZED VIEW demo.sales_summary AS
SELECT user_id, SUM(amount) AS total FROM demo.orders GROUP BY user_id;
REFRESH MATERIALIZED VIEW demo.sales_summary;
SELECT user_id, total FROM demo.sales_summary ORDER BY user_id;
ROLLBACK;

PREPARE demo_user_query (bigint) AS
SELECT username FROM demo.users WHERE id = $1;
EXECUTE demo_user_query(1);
DEALLOCATE demo_user_query;
```

Ожидаются итоги `1 | 140.00`, `2 | 300.00` и имя `alice`.
Материализованное представление хранит снимок результата и требует обновления;
обычное VIEW хранит запрос. TEMP-таблица живёт в сеансе или до конца транзакции по ON COMMIT.
PREPARE привязан к сеансу; в приложении обычно удобнее параметры/подготовка через драйвер.

## Источники

- [Типы](https://www.postgresql.org/docs/18/datatype.html), [identity](https://www.postgresql.org/docs/18/ddl-identity-columns.html), [ограничения](https://www.postgresql.org/docs/18/ddl-constraints.html), [ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html).
- [Типы индексов](https://www.postgresql.org/docs/18/indexes-types.html), [CREATE INDEX / CONCURRENTLY](https://www.postgresql.org/docs/18/sql-createindex.html), [EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html).
- [JSON и JSONB](https://www.postgresql.org/docs/18/functions-json.html), [FTS-индексы](https://www.postgresql.org/docs/18/textsearch-tables.html).
- [Партиционирование](https://www.postgresql.org/docs/18/ddl-partitioning.html), [материализованные представления](https://www.postgresql.org/docs/18/rules-materializedviews.html).
