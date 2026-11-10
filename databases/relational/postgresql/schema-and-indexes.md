# Проектировать схему, индексы и поиск

Откройте страницу для ограничений данных, изменения схемы и выбора индекса в PostgreSQL 18.
Исполняемые фрагменты продолжают учебную схему `demo`; план и блокировки зависят от нагрузки.

<a id="навигация"></a>

## Быстрый поиск

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Выбрать представление и допустимые данные | Типы, identity, FK и CHECK | [Типы и ограничения](#типы-и-ограничения) |
| Изменить структуру и проверить откат | ALTER TABLE в транзакции | [Изменение схемы](#изменить-таблицу-и-схему) |
| Подобрать индекс по фильтру и сортировке | B-tree, частичный индекс и EXPLAIN | [Индексы](#индексы-и-план-запроса) |
| Искать по JSON или словам текста | JSONB и FTS с GIN | [Поиск](#jsonb-и-полнотекстовый-поиск) |
| Разместить данные по диапазонам дат | RANGE-партиции | [Партиционирование](#партиционирование) |
| Сохранить итог или подготовить запрос сеанса | MATERIALIZED VIEW и PREPARE | [Представления](#представления-и-подготовленные-запросы) |

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — типы/ограничения; средний — DDL/индексы; продвинутый — JSONB/FTS/партиции |
| Предпосылки | PostgreSQL 18; БД `cheatsheet_demo` и схема из [queries.sql](query-lab.md#полный-пример-учебная-база); подключение владельцем |

## Типы и ограничения

Данные должны сохранять точность чисел, смысл времени и допустимые связи.
Выберите тип и ограничение по этим требованиям.

**Базовый уровень.** Основная схема уже показана в полном примере.
Ниже приведена справочная таблица типов.

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

`CHECK (price >= 0)` сам по себе допускает NULL.
Если NULL недопустим, добавьте NOT NULL.
PRIMARY KEY/UNIQUE создают индекс для обеспечения уникальности.
Не дублируйте этот индекс вручную.
Внешний ключ не создаёт автоматически индекс на ссылающемся столбце.
Оцените необходимость индекса по запросам и удалениям.
`ON DELETE CASCADE` удаляет связанные строки.
`RESTRICT` запрещает удаление используемой записи.

## Изменить таблицу и схему

Учебной схеме нужны новый столбец, точность цены и запрет пустого имени.
Сначала проверьте изменения с откатом.

**Средний уровень.** Выполните фрагмент SQL в `cheatsheet_demo`.
Фрагмент откатывает изменения учебной таблицы:

```sql
BEGIN;
ALTER TABLE demo.users ADD COLUMN phone text;
ALTER TABLE demo.products ALTER COLUMN price TYPE numeric(12, 2);
ALTER TABLE demo.products ADD CONSTRAINT products_name_nonempty CHECK (name <> '');
ALTER TABLE demo.users RENAME COLUMN phone TO phone_number;
ROLLBACK;
```

После отката столбца phone/phone_number нет, price остаётся numeric(10, 2).
ALTER TABLE может блокировать доступ и переписывать данные.
Отдельно проверьте возможность безопасного преобразования большой таблицы.
После фиксации удаление COLUMN/CONSTRAINT приводит к необратимой потере данных или защиты.
CASCADE может удалить зависимые объекты.

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

Запрос выбирает заказы пользователя и сортирует по дате; отдельно нужен поиск неоплаченных заказов.
Проверьте составной и частичный индексы по реальному плану.

**Средний уровень.** Фрагмент SQL после queries.sql. Создаёт два учебных индекса один раз:

```sql
CREATE INDEX orders_user_date_idx ON demo.orders (user_id, ordered_at);
CREATE INDEX orders_pending_idx ON demo.orders (ordered_at) WHERE status = 'pending';

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, amount FROM demo.orders
WHERE user_id = 1 ORDER BY ordered_at;
```

Проверьте индексы командой `psql` `\d demo.orders`.
План зависит от статистики, объёма и настроек.
На трёх строках последовательное чтение нормально.
EXPLAIN ANALYZE **выполняет** запрос.
Изменяющий запрос создаст реальные побочные эффекты.
Начните оптимизацию с плана и измерений.
Общий запрет последовательного чтения не заменяет измерения.

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

**Продвинутый уровень.** Замените имена в общих формах ниже.
CONCURRENTLY позволяет не блокировать обычные записи на всё время построения.
Построение с CONCURRENTLY длится дольше, имеет ограничения и может ждать транзакции.
CONCURRENTLY не означает параллельное построение.
Выполняйте CONCURRENTLY вне явного блока транзакции.
После ошибки проверьте, не остался ли невалидный индекс.

```text
CREATE INDEX CONCURRENTLY index_name ON schema_name.table_name (column_name);
REINDEX INDEX schema_name.index_name;
REINDEX INDEX CONCURRENTLY schema_name.index_name;
ALTER INDEX schema_name.index_name RENAME TO new_index_name;
DROP INDEX schema_name.index_name;  -- удалит индекс; проверьте зависимости и нагрузку
```

## JSONB и полнотекстовый поиск

Профиль содержит вложенные поля, а описание товара — слова для поиска.
Сопоставьте структуру данных и нужный оператор.

**Продвинутый уровень.** Фрагменты SQL на demo-схеме. Первые запросы не меняют данные:

```sql
SELECT username, profile->>'city' AS city
FROM demo.users
WHERE profile @> '{"tags":["vip"]}'::jsonb;

SELECT username FROM demo.users WHERE profile ? 'city' ORDER BY username;

SELECT name FROM demo.products
WHERE to_tsvector('english', description) @@ plainto_tsquery('english', 'keyboard');
```

Первый запрос возвращает `alice | Moscow`.
Второй запрос возвращает `alice`, `bob`.
Третий запрос возвращает товар `Keyboard`.
`->` возвращает JSON/JSONB.
`->>` возвращает текст.
Операторы `?`, `@>` и конкатенация `||` здесь относятся к JSONB.
Не переносите эти операции на json без проверки.
Для обновления вложенного значения используйте `jsonb_set`.
Для сборки и агрегации используйте `jsonb_build_object`, `jsonb_agg`, `jsonb_object_agg`.

Следующий фрагмент SQL создаёт постоянные учебные индексы один раз:

```sql
CREATE INDEX users_profile_gin ON demo.users USING GIN (profile);
CREATE INDEX products_fts_gin ON demo.products
USING GIN (to_tsvector('english', description));
```

Проверьте индексы через `\d demo.users` и `\d demo.products` в psql.
Для применения FTS-индекса выражение и конфигурация запроса должны соответствовать индексу.
Для русских текстов выберите подходящую конфигурацию, например `russian`.
Для данных примера выбран `english`.
Полнотекстовый поиск встроен.
unaccent/pg_trgm решают дополнительные задачи и не требуются для включения FTS.

## Партиционирование

Измерения приходят по датам; данные ноября нужно направить в отдельную партицию.

**Продвинутый уровень.** Самостоятельный фрагмент SQL выполняется в `cheatsheet_demo`.
Фрагмент создаёт новую таблицу в demo:

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

Ожидается `demo.measurements_2026_11 | 2026-11-06`.
После отката таблиц нет.
Начальная граница включена, конечная исключена.
Если нет подходящей/default-партиции, строка вне существующих диапазонов даст ошибку.
Декларативное партиционирование и наследование `INHERITS` — разные механизмы.
Партиционирование требует плана создания и удаления партиций.
Партиционирование не гарантирует ускорение любого запроса.

## Представления и подготовленные запросы

Итоги заказов нужны как обновляемый снимок; запрос пользователя повторяется в одном сеансе.

**Средний / продвинутый уровень.** Фрагмент SQL использует схему demo.
Фрагмент откатывает изменения схемы:

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
Материализованное представление хранит снимок результата и требует обновления.
Обычное VIEW хранит запрос.
TEMP-таблица живёт в сеансе или до конца транзакции по ON COMMIT.
PREPARE привязан к сеансу.
В приложении обычно удобнее использовать параметры или подготовку через драйвер.

## Источники

- [Типы](https://www.postgresql.org/docs/18/datatype.html), [identity](https://www.postgresql.org/docs/18/ddl-identity-columns.html), [ограничения](https://www.postgresql.org/docs/18/ddl-constraints.html), [ALTER TABLE](https://www.postgresql.org/docs/18/sql-altertable.html).
- [Типы индексов](https://www.postgresql.org/docs/18/indexes-types.html), [CREATE INDEX / CONCURRENTLY](https://www.postgresql.org/docs/18/sql-createindex.html), [EXPLAIN](https://www.postgresql.org/docs/18/using-explain.html).
- [JSON и JSONB](https://www.postgresql.org/docs/18/functions-json.html), [FTS-индексы](https://www.postgresql.org/docs/18/textsearch-tables.html).
- [Партиционирование](https://www.postgresql.org/docs/18/ddl-partitioning.html), [материализованные представления](https://www.postgresql.org/docs/18/rules-materializedviews.html).
