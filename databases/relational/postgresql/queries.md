# Выбирать, изменять и анализировать данные

Откройте страницу для выборки, изменения и анализа заказов в PostgreSQL 18.
Зависимые фрагменты используют учебную схему `demo`; подготовка находится в отдельном полном примере.

## Быстрый поиск

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Посчитать оплаты для всех пользователей | LEFT JOIN с фильтром в ON | [Короткий пример](#посчитать-оплаты-всех-пользователей) |
| Отобрать товары и найти пользователя без заказов | WHERE, JOIN, NOT EXISTS | [Выборка](#выбрать-строки-и-объединить-таблицы) |
| Получить изменённую строку или сделать upsert | RETURNING и ON CONFLICT | [Изменения](#изменить-данные-и-проверить-результат) |
| Посчитать итоги, ранги и предыдущую сумму | GROUP BY, CTE и окна | [Аналитика](#группы-cte-и-оконные-функции) |
| Обойти известное дерево | WITH RECURSIVE | [Обход](#рекурсивный-обход) |
| Выбрать строковую, числовую или временную функцию | Таблица выражений с результатами | [Функции](#функции-для-повседневных-запросов) |

[К справочнику PostgreSQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — полный пример и CRUD; средний — группы/окна; продвинутый — рекурсия |
| Предпосылки | PostgreSQL 18, `createdb`, `psql`; роль с правом создать учебную БД |

## Навигация

- [Посчитать оплаты всех пользователей](#посчитать-оплаты-всех-пользователей)
- [Полный SQL и запуск](query-lab.md#полный-пример-учебная-база)
- [Выбрать строки и объединить таблицы](#выбрать-строки-и-объединить-таблицы)
- [Изменить данные и проверить результат](#изменить-данные-и-проверить-результат)
- [Группы, CTE и оконные функции](#группы-cte-и-оконные-функции)
- [Рекурсивный обход](#рекурсивный-обход)
- [Функции для повседневных запросов](#функции-для-повседневных-запросов)
- [Источники](#источники)

<a id="полный-пример-учебная-база"></a>

## Посчитать оплаты всех пользователей

**Когда:** нужны итоги заказов по всем пользователям, включая пользователей без заказов.
Подготовьте `demo.users`, `demo.products` и `demo.orders` по [полному SQL и запуску](query-lab.md#полный-пример-учебная-база).
Фрагмент PostgreSQL 18 после этой подготовки:

```sql
SELECT u.username, COALESCE(SUM(o.amount), 0) AS paid_total
FROM demo.users AS u
LEFT JOIN demo.orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.username
ORDER BY u.username;
```

**Результат:** `alice | 140.00`, `bob | 300.00`, `carol | 0`.
Условие в `ON` сохраняет пользователей без оплаченных заказов.
Эта схема показывает запросы и ограничения; схема не задаёт полный алгоритм продажи.
Все зависимые фрагменты страницы выполняются в `cheatsheet_demo` после подготовки.

## Выбрать строки и объединить таблицы

Нужны товары заданной цены, состав заказов или пользователи без заказов.

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

Нужно изменить конкретную запись и получить её фактическое новое значение.

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

Нужны суммы по пользователям и позиция каждого заказа без потери строк.

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

Данные образуют известное дерево руководителей без циклов.
Нужно вернуть сотрудника и глубину от корня.

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
