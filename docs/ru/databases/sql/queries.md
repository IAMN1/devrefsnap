
# Запросы на согласованном наборе данных

[English](../../../en/databases/sql/queries.md)

Откройте страницу для выборки, изменения и расчётов по связанным таблицам.
Фрагменты PostgreSQL/SQLite используют общий учебный набор; подготовка вынесена отдельно.


## Быстрый поиск

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Посчитать оплаты без потери пользователей | LEFT JOIN и условие в ON | [Итоги по пользователям](#посчитать-оплаты-без-потери-пользователей) |
| Отобрать строки и найти отсутствующие связи | WHERE, JOIN, NOT EXISTS | [Выборка](#фильтрация-и-соединения) |
| Изменить связанные строки с откатом | Транзакция и CRUD | [Изменения](#изменение-данных) |
| Получить итоги и положение каждой строки | GROUP BY, CTE, окна | [Аналитика](#агрегация-cte-и-окна) |

[К SQL](README.md)

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — CRUD/фильтры; средний — JOIN/группы; продвинутый — окна/рекурсия |
| Предпосылки | Новая учебная БД PostgreSQL 18 или SQLite 3.53; имена sql_users/sql_orders свободны |

<a id="полный-пример"></a>


## Посчитать оплаты без потери пользователей

**Когда:** нужно соединять пользователей `sql_users` и заказы `sql_orders`, сохранив пользователей без оплаченных заказов.
Подготовьте таблицы по [полному SQL и командам запуска](query-lab.md#полный-пример).
Фрагмент PostgreSQL/SQLite после этой подготовки:

```sql
SELECT u.name, COALESCE(SUM(o.amount_cents), 0) AS paid_cents
FROM sql_users AS u
LEFT JOIN sql_orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.name
ORDER BY u.name;
```

**Результат:** `alice | 14000`, `bob | 0`, `carol | 0`.
Условие `status` в `ON` сохраняет пользователей без оплаченных заказов.
Перенос этого условия в `WHERE` удалит таких пользователей.
Суммы хранятся целыми условными центами.
Все зависимые фрагменты страницы используют подготовленные таблицы в той же БД.


## Фильтрация и соединения

Нужны заказы в диапазоне сумм или пользователи без заказов.
Фрагменты используют [учебный набор](query-lab.md#полный-пример) и не меняют данные.

**Базовый / средний уровень.** Независимые фрагменты без изменения данных:

```sql
SELECT id, amount_cents FROM sql_orders
WHERE status IN ('paid', 'pending')
  AND amount_cents BETWEEN 4000 AND 10000
ORDER BY amount_cents DESC, id;

SELECT u.name, o.amount_cents
FROM sql_users AS u JOIN sql_orders AS o ON o.user_id = u.id
WHERE NOT (o.status = 'pending') ORDER BY o.id;

SELECT u.name FROM sql_users AS u
WHERE NOT EXISTS (SELECT 1 FROM sql_orders AS o WHERE o.user_id = u.id);

SELECT id FROM sql_users
EXCEPT
SELECT user_id FROM sql_orders;
```

Первый запрос возвращает заказы `1 | 10000`, `2 | 4000`.
Второй запрос возвращает `alice | 10000`, `alice | 4000`.
Пользователь без заказов — `carol`.
Разность множеств содержит id `3`.
Скобки уточняют сочетания AND/OR/NOT.
BETWEEN включает обе границы.
В LIKE `%` обозначает любое число символов, а `_` — один символ.
Проверяйте NULL через IS NULL.

| Соединение / операция | Назначение / ограничение |
| --- | --- |
| INNER JOIN | Совпавшие строки; не обязательно «пересечение множеств» при дубликатах |
| LEFT / RIGHT / FULL JOIN | Сохранение несовпавших строк слева / справа / с обеих сторон; FULL JOIN отсутствует в MySQL 8.4 |
| CROSS JOIN | Все сочетания; размер результата может резко вырасти |
| SELF JOIN | Обычное соединение таблицы с собой через разные псевдонимы |
| USING (id) | Соединение по одноимённым столбцам; не поддерживается этим синтаксисом в SQL Server |
| NATURAL JOIN | Соединяет по всем общим именам; добавление столбца способно незаметно изменить смысл |
| UNION / UNION ALL | Объединение с удалением / сохранением дубликатов |
| INTERSECT / EXCEPT | Общие строки / строки слева без строк справа; проверьте поддержку ветки СУБД |

Подзапрос в WHERE задаёт IN/EXISTS или сравнение.
Подзапрос в FROM задаёт производную таблицу с alias.
Подзапрос в SELECT задаёт скалярное значение одного столбца.
PostgreSQL отклоняет скалярный подзапрос, который вернул несколько строк.
SQLite берёт первую строку.
Для переносимого результата обеспечьте одну строку по смыслу запроса, например условием по UNIQUE-ключу.
Пустой результат даёт NULL.
Не считайте любой коррелированный подзапрос медленным.
Проверьте план.


## Изменение данных

Нужно добавить пользователя и заказ, проверить изменение и вернуть исходные данные.

**Базовый уровень.** Фрагмент PostgreSQL/SQLite: изменения откатываются целиком.
До запуска проверьте, что выбрана учебная БД.
Без WHERE UPDATE/DELETE затронут все строки.

```sql
BEGIN;
INSERT INTO sql_users (id, name) VALUES (4, 'dave');
INSERT INTO sql_orders (id, user_id, amount_cents, status)
SELECT 4, id, 500, 'pending' FROM sql_users WHERE name = 'dave';
UPDATE sql_orders SET status = 'paid', amount_cents = 600 WHERE id = 4;
SELECT amount_cents, status FROM sql_orders WHERE id = 4;
DELETE FROM sql_orders WHERE id = 4;
DELETE FROM sql_users WHERE id = 4;
ROLLBACK;
```

Промежуточный SELECT возвращает `600 | paid`.
После отката исходное число строк остаётся 3/3.
Возврат изменённых строк (`RETURNING`/`OUTPUT`) и UPDATE с JOIN разбираются в [диалектах](dialects-and-transactions.md#различия-диалектов).
ON DELETE CASCADE действует только если объявлен внешний ключ с таким действием и проверки включены.


## Агрегация, CTE и окна

Нужны итоги по пользователям и накопительная сумма без объединения строк результата.

**Средний уровень.** Фрагменты PostgreSQL/SQLite на учебных данных:

```sql
WITH totals AS (
    SELECT user_id, COUNT(*) AS orders, SUM(amount_cents) AS total
    FROM sql_orders
    GROUP BY user_id HAVING COUNT(*) >= 2
)
SELECT u.name, t.orders, t.total
FROM totals AS t JOIN sql_users AS u ON u.id = t.user_id;

SELECT id, amount_cents,
       ROW_NUMBER() OVER (ORDER BY amount_cents DESC, id) AS position,
       SUM(amount_cents) OVER (
           ORDER BY id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_cents,
       LAG(amount_cents) OVER (ORDER BY id) AS previous_cents
FROM sql_orders ORDER BY id;
```

Первый результат — `alice | 2 | 14000`. Второй:

| id | amount_cents | position | running_cents | previous_cents |
| --- | --- | --- | --- | --- |
| 1 | 10000 | 2 | 10000 | NULL |
| 2 | 4000 | 3 | 14000 | 10000 |
| 3 | 30000 | 1 | 44000 | 4000 |

COUNT, SUM, AVG, MIN/MAX работают с группой.
Большинство агрегатов пропускают NULL.
CTE именует промежуточный запрос, но само по себе не обещает материализацию или ускорение.
Для подзапроса в FROM производную таблицу именуют явно, например `FROM (...) AS totals`.

**Продвинутый уровень.** PARTITION BY делит окно на группы.
ORDER BY внутри OVER задаёт порядок расчёта.
Этот ORDER BY не задаёт порядок вывода всего SELECT.
RANK оставляет пропуски после равенств.
DENSE_RANK не оставляет пропуски.
LEAD смотрит вперёд.
FIRST_VALUE/LAST_VALUE зависят от фрейма.
`ROWS 6 PRECEDING` считает строки, а не дни.
Для LAST_VALUE всей группы нужен фрейм до UNBOUNDED FOLLOWING.
При расчёте доли суммы защитите деление от нуля.
Выберите подходящий дробный тип.
Правила целочисленного деления различаются между СУБД.

Самостоятельный фрагмент PostgreSQL/SQLite, без зависимостей от таблиц:

```sql
WITH RECURSIVE numbers(n) AS (
    SELECT 1
    UNION ALL
    SELECT n + 1 FROM numbers WHERE n < 3
)
SELECT n FROM numbers ORDER BY n;
```

Результат — `1`, `2`, `3`. Для графов нужны обнаружение циклов и ограничение глубины.
В SQL Server рекурсивный CTE записывается без слова RECURSIVE и имеет собственные ограничения.


## Источники

- [PostgreSQL: JOIN/группы](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTE](https://www.postgresql.org/docs/18/queries-with.html), [окна](https://www.postgresql.org/docs/18/functions-window.html).
- [SQLite: SELECT](https://www.sqlite.org/lang_select.html), [WITH](https://www.sqlite.org/lang_with.html), [окна](https://www.sqlite.org/windowfunctions.html).
- [SQLite: scalar subquery](https://www.sqlite.org/lang_expr.html#subquery_expressions), [PostgreSQL: scalar subquery](https://www.postgresql.org/docs/18/sql-expressions.html#SQL-SYNTAX-SCALAR-SUBQUERIES).
- [MySQL 8.4: JOIN](https://dev.mysql.com/doc/refman/8.4/en/join.html), [SQL Server: CTE](https://learn.microsoft.com/en-us/sql/t-sql/queries/with-common-table-expression-transact-sql?view=sql-server-ver17).
- [PostgreSQL 18.6: release notes](https://www.postgresql.org/docs/18/release-18-6.html), [SQLite 3.53.4: release notes](https://www.sqlite.org/releaselog/3_53_4.html).
