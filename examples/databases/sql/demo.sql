BEGIN;
CREATE TABLE sql_users (
    id integer PRIMARY KEY,
    name varchar(80) NOT NULL UNIQUE
);
CREATE TABLE sql_orders (
    id integer PRIMARY KEY,
    user_id integer NOT NULL REFERENCES sql_users(id),
    amount_cents integer NOT NULL CHECK (amount_cents >= 0),
    status varchar(20) NOT NULL CHECK (status IN ('paid', 'pending'))
);
INSERT INTO sql_users (id, name) VALUES (1, 'alice'), (2, 'bob'), (3, 'carol');
INSERT INTO sql_orders (id, user_id, amount_cents, status) VALUES
    (1, 1, 10000, 'paid'), (2, 1, 4000, 'paid'), (3, 2, 30000, 'pending');

SELECT u.name, COALESCE(SUM(o.amount_cents), 0) AS paid_cents
FROM sql_users AS u
LEFT JOIN sql_orders AS o ON o.user_id = u.id AND o.status = 'paid'
GROUP BY u.id, u.name
ORDER BY u.name;

SAVEPOINT before_change;
UPDATE sql_orders SET amount_cents = 1 WHERE id = 1;
ROLLBACK TO SAVEPOINT before_change;
RELEASE SAVEPOINT before_change;
COMMIT;

SELECT amount_cents AS preserved_amount FROM sql_orders WHERE id = 1;
