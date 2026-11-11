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
