# Выбирать, изменять и анализировать данные

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — полный пример и CRUD; средний — группы/окна; продвинутый — рекурсия |
| Предпосылки | PostgreSQL 18, `createdb`, `psql`; роль с правом создать учебную БД |
| Сверено с документацией | 2026-11-06, PostgreSQL 18 |
| Выполнено | 2026-11-06, PostgreSQL 18.6 / PGlite 0.5.15, в памяти, WebAssembly: все SQL-блоки страницы; проверены JOIN/суммы, данные после отката, оконные результаты |
| Не проверено | Команды createdb/psql и выполнение на нативном сервере; конкурентные сеансы |

## Навигация

- [Полный пример: учебная база](#полный-пример-учебная-база)
- [Выбрать строки и объединить таблицы](#выбрать-строки-и-объединить-таблицы)
- [Изменить данные и проверить результат](#изменить-данные-и-проверить-результат)
- [Группы, CTE и оконные функции](#группы-cte-и-оконные-функции)
- [Рекурсивный обход](#рекурсивный-обход)
- [Функции для повседневных запросов](#функции-для-повседневных-запросов)
- [Источники](#источники)

## Полный пример: учебная база

**Базовый уровень.** Подготовьте отдельный учебный сервер или кластер.
Команды оболочки ниже рассчитаны на локальный сервер с ролью `postgres`.
При другой установке замените адрес и роль.
Пароль вводится по запросу или берётся из настроенного password file.

Сохраните следующий полный SQL-блок как `queries.sql` в текущем каталоге.
Запустите команды оболочки ниже.
Первая команда создаст новую БД.
Если имя уже занято, команда завершится ошибкой.
Существующие данные не удаляются.

```bash
createdb --host=127.0.0.1 --username=postgres --template=template0 cheatsheet_demo && \
psql --host=127.0.0.1 --username=postgres --dbname=cheatsheet_demo \
  --no-psqlrc --set=ON_ERROR_STOP=1 --file=queries.sql
```

Полный пример использует диалект PostgreSQL 18.
Пример создаёт постоянную схему `demo` и данные в одной транзакции.
Повторный запуск в той же БД остановится на существующей схеме.
Скрипт не удаляет объекты.

<!-- example: queries.sql -->
```sql
BEGIN;

CREATE SCHEMA demo;

CREATE TABLE demo.users (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username text NOT NULL UNIQUE,
    email text NOT NULL UNIQUE,
    is_active boolean NOT NULL DEFAULT true,
    profile jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE demo.products (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name text NOT NULL,
    price numeric(10, 2) NOT NULL CHECK (price >= 0),
    stock integer NOT NULL CHECK (stock >= 0),
    description text NOT NULL DEFAULT ''
);

CREATE TABLE demo.orders (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES demo.users(id) ON DELETE RESTRICT,
    product_id bigint NOT NULL REFERENCES demo.products(id) ON DELETE RESTRICT,
    amount numeric(10, 2) NOT NULL CHECK (amount > 0),
    status text NOT NULL CHECK (status IN ('pending', 'paid', 'cancelled')),
    ordered_at timestamptz NOT NULL
);

INSERT INTO demo.users (username, email, profile) VALUES
    ('alice', 'alice@example.test', '{"city":"Moscow","tags":["vip"]}'),
    ('bob', 'bob@example.test', '{"city":"Kazan"}'),
    ('carol', 'carol@example.test', '{}');

INSERT INTO demo.products (name, price, stock, description) VALUES
    ('Keyboard', 100.00, 10, 'Mechanical keyboard'),
    ('Mouse', 40.00, 5, 'Wireless mouse'),
    ('Monitor', 300.00, 2, 'Large monitor');

INSERT INTO demo.orders (user_id, product_id, amount, status, ordered_at) VALUES
    (1, 1, 100.00, 'paid', '2026-11-01 12:00:00+00'),
    (1, 2, 40.00, 'paid', '2026-11-02 12:00:00+00'),
    (2, 3, 300.00, 'paid', '2026-11-03 12:00:00+00');

SELECT u.username, COALESCE(SUM(o.amount), 0) AS paid_total
FROM demo.users AS u
LEFT JOIN demo.orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.username
ORDER BY u.username;

SAVEPOINT before_stock_change;
UPDATE demo.products SET stock = stock - 1
WHERE id = 1 AND stock > 0
RETURNING name, stock;
ROLLBACK TO SAVEPOINT before_stock_change;

SELECT stock = 10 AS rollback_ok
FROM demo.products WHERE id = 1;

COMMIT;
```

**Ожидаемый результат:** суммы `alice | 140.00`, `bob | 300.00`, `carol | 0`.
`RETURNING` возвращает `Keyboard | 9`.
`rollback_ok` равен `t`.
После COMMIT исходный остаток равен `10`.
Заказы здесь — учебные записи, а не полный алгоритм продажи со списанием товара.

Все следующие фрагменты выполняются в соединении с `cheatsheet_demo` после этого примера.
Используется явная схема `demo`, поэтому результат не зависит от `search_path`.

## Выбрать строки и объединить таблицы

**Базовый уровень.** Независимые фрагменты SQL на учебной схеме:

```sql
SELECT id, name, price
FROM demo.products
WHERE price BETWEEN 40 AND 100
ORDER BY price, id
LIMIT 10 OFFSET 0;

SELECT o.id, u.username, p.name, o.amount
FROM demo.orders AS o
JOIN demo.users AS u ON u.id = o.user_id
JOIN demo.products AS p ON p.id = o.product_id
WHERE o.status = 'paid'
ORDER BY o.id;

SELECT u.username
FROM demo.users AS u
WHERE NOT EXISTS (SELECT 1 FROM demo.orders AS o WHERE o.user_id = u.id);
```

Первый запрос возвращает товары `Mouse`, `Keyboard`.
Второй запрос возвращает три заказа в порядке id.
Пользователь без заказов — `carol`.
`INNER JOIN` оставляет совпадения.
`LEFT JOIN` сохраняет строки слева.
`RIGHT JOIN` сохраняет строки справа.
`FULL JOIN` сохраняет строки с обеих сторон.
`CROSS JOIN` строит все сочетания.
При LEFT JOIN фильтр правой таблицы в WHERE может удалить строки без совпадений.
Поэтому в полном примере фильтр `status` находится в ON.

`UNION` удаляет дубликаты.
`UNION ALL` сохраняет дубликаты.
`INTERSECT` оставляет общие строки.
`EXCEPT` оставляет строки первого результата без строк второго.
Результаты должны иметь одинаковое число столбцов с совместимыми типами.
`IS NULL` проверяет отсутствие значения.
Сравнение `= NULL` для такой проверки не подходит.

## Изменить данные и проверить результат

**Базовый / средний уровень.** Фрагменты SQL независимы и завершаются ROLLBACK.
Фрагменты временно меняют данные.
Счётчик identity может увеличиться даже после отката.

```sql
BEGIN;
INSERT INTO demo.users (username, email)
VALUES ('dave', 'dave@example.test')
RETURNING id, username;
ROLLBACK;

BEGIN;
INSERT INTO demo.users (username, email)
VALUES ('alice', 'alice@example.test')
ON CONFLICT (username) DO UPDATE SET email = EXCLUDED.email
RETURNING username, email;
ROLLBACK;

BEGIN;
UPDATE demo.products SET price = price * 1.10
WHERE id = 2 RETURNING name, price;
ROLLBACK;

BEGIN;
DELETE FROM demo.users AS u
WHERE u.username = 'carol'
  AND NOT EXISTS (SELECT 1 FROM demo.orders AS o WHERE o.user_id = u.id)
RETURNING username;
ROLLBACK;
```

Ожидаются `dave` с новым id, `alice | alice@example.test`, `Mouse | 44.00`, `carol`.
После каждого отката данные остаются прежними.
Для upsert нужен подходящий UNIQUE/PK.
Конфликт по другому ограничению, например email, всё ещё может дать ошибку.
INSERT из SELECT имеет вид `INSERT INTO target (col1, col2) SELECT col1, col2 FROM source`.
Это схема записи без привязки к демонстрационным таблицам.

Перед массовым UPDATE/DELETE сначала проверьте тот же WHERE через SELECT.
Без WHERE изменятся все строки.
`TRUNCATE` удаляет все строки и блокирует таблицу эксклюзивно.
`TRUNCATE` допускает откат.
С CASCADE также очищаются связанные таблицы.
Эти команды не нужны для запуска примеров.

## Группы, CTE и оконные функции

**Средний уровень.** Независимые фрагменты SQL, данные не меняются:

```sql
WITH totals AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total
    FROM demo.orders
    GROUP BY user_id
    HAVING COUNT(*) >= 2
)
SELECT u.username, t.order_count, t.total
FROM totals AS t JOIN demo.users AS u ON u.id = t.user_id;

SELECT id, amount,
       ROW_NUMBER() OVER (ORDER BY amount DESC, id) AS position,
       SUM(amount) OVER (
           ORDER BY ordered_at, id
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total,
       LAG(amount) OVER (ORDER BY ordered_at, id) AS previous_amount
FROM demo.orders
ORDER BY ordered_at, id;
```

Первый запрос даёт `alice | 2 | 140.00`. Второй:

| id | amount | position | running_total | previous_amount |
| --- | --- | --- | --- | --- |
| 1 | 100.00 | 2 | 100.00 | NULL |
| 2 | 40.00 | 3 | 140.00 | 100.00 |
| 3 | 300.00 | 1 | 440.00 | 40.00 |

`PARTITION BY user_id` выполняет расчёт отдельно по пользователям.
`RANK` оставляет пропуски после равных мест.
`DENSE_RANK` не оставляет пропуски.
Дополнительные поля сортировки влияют на равенство мест.
`LEAD` смотрит вперёд.
`AVG(...) OVER (...)` считает среднее по окну.
Для доли используйте `amount / NULLIF(SUM(amount) OVER (), 0)`.
Здесь amount имеет тип numeric.

`ROWS BETWEEN 6 PRECEDING AND CURRENT ROW` — семь строк, а не семь календарных дней.
Для интервала по времени выберите подходящий RANGE и поле времени.
Для соседних групп равных ключей используйте GROUPS.
Результат `LAST_VALUE` зависит от фрейма.
Для последнего элемента всей группы задайте `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.

## Рекурсивный обход

**Продвинутый уровень.** Ниже приведён самостоятельный фрагмент SQL.
Фрагмент не требует дополнительных таблиц:

```sql
WITH RECURSIVE employees(id, name, manager_id) AS (
    VALUES (1, 'Lead', NULL::integer), (2, 'Developer', 1), (3, 'Intern', 2)
), tree AS (
    SELECT id, name, manager_id, 1 AS depth
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, t.depth + 1
    FROM employees AS e JOIN tree AS t ON e.manager_id = t.id
)
SELECT name, depth FROM tree ORDER BY depth, id;
```

Результат: `Lead | 1`, `Developer | 2`, `Intern | 3`.
Для произвольного графа задайте ограничения глубины или обнаружение циклов, например `CYCLE`.
Простая рекурсия выше предназначена для известного дерева.

## Функции для повседневных запросов

**Базовый / средний уровень.** Таблица содержит самостоятельные выражения SELECT или формы функций.
Замените поля в общих формах своими.

| Задача | Пример / форма | Результат или ограничение |
| --- | --- | --- |
| Строки | `SELECT POSITION('SQL' IN 'PostgreSQL');` | `8`, позиции считаются с 1 |
| Подстрока | `SELECT SUBSTRING('PostgreSQL' FROM 1 FOR 4);` | `Post` |
| Обработка текста | `LOWER`, `UPPER`, `TRIM`, `REPLACE`, `CONCAT`, `STRING_TO_ARRAY`, `UNNEST` | `CONCAT` и оператор `||` по-разному обрабатывают NULL |
| Точное округление | `SELECT ROUND(123.456, 2);` | `123.46`; перегрузка с двумя аргументами принимает numeric |
| Математика | `ABS`, `CEIL`, `FLOOR`, `POWER`, `SQRT`, `LN`, `LOG`, `MOD` | Сверяйте типы аргументов; целочисленное деление отбрасывает дробь |
| Псевдослучайное число | `SELECT RANDOM();` | `0 <= x < 1`; не для секретов |
| Начало месяца | `SELECT DATE_TRUNC('month', TIMESTAMP '2026-11-06 14:30');` | `2026-11-01 00:00:00` |
| Текущее время | `CURRENT_DATE`, `CURRENT_TIMESTAMP`, `NOW()` | Timestamp соответствует началу транзакции; для текущего момента есть `clock_timestamp()` |
| Разбор / форматирование | `EXTRACT`, `TO_CHAR`, `TO_DATE`, `TO_TIMESTAMP`, `AGE` | Учитывайте тип и часовой пояс |
| Условия и NULL | `CASE`, `COALESCE`, `NULLIF`, `GREATEST`, `LEAST` | `COALESCE` выбирает первое не-NULL значение |

## Источники

- [INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html), [UPDATE](https://www.postgresql.org/docs/18/sql-update.html), [DELETE](https://www.postgresql.org/docs/18/sql-delete.html).
- [JOIN и группировка](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTE и рекурсия](https://www.postgresql.org/docs/18/queries-with.html).
- [Оконные функции](https://www.postgresql.org/docs/18/functions-window.html), [фреймы окон](https://www.postgresql.org/docs/18/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).
- [Строковые функции](https://www.postgresql.org/docs/18/functions-string.html), [математика](https://www.postgresql.org/docs/18/functions-math.html), [дата и время](https://www.postgresql.org/docs/18/functions-datetime.html).
