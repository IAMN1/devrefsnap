# Подготовить учебную базу PostgreSQL

Пример создаёт пользователей, товары и заказы для карточек PostgreSQL.
Используйте отдельный PostgreSQL 18 и новое имя БД `cheatsheet_demo`.
[К карточкам запросов](queries.md) · [К PostgreSQL](README.md).

| Задача | Приём | Пример |
| --- | --- | --- |
| Создать исходные данные и проверить результат | Полный учебный сценарий | [Код и запуск](#полный-пример-учебная-база) |

| Параметр | Значение |
| --- | --- |
| Уровни | Базовый — схема и данные; средний — JOIN и savepoint |
| Предпосылки | PostgreSQL 18, `createdb`, `psql`; роль с правом создать учебную БД |

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

[Карточки запросов](queries.md) выполняются в `cheatsheet_demo` после этого примера.
Используется явная схема `demo`, поэтому результат не зависит от `search_path`.

## Источники

- [INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html), [UPDATE](https://www.postgresql.org/docs/18/sql-update.html), [DELETE](https://www.postgresql.org/docs/18/sql-delete.html).
- [JOIN и группировка](https://www.postgresql.org/docs/18/queries-table-expressions.html), [CTE и рекурсия](https://www.postgresql.org/docs/18/queries-with.html).
- [Оконные функции](https://www.postgresql.org/docs/18/functions-window.html), [фреймы окон](https://www.postgresql.org/docs/18/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS).
- [Строковые функции](https://www.postgresql.org/docs/18/functions-string.html), [математика](https://www.postgresql.org/docs/18/functions-math.html), [дата и время](https://www.postgresql.org/docs/18/functions-datetime.html).
