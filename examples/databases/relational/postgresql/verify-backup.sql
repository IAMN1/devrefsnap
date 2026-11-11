BEGIN;
DO $check$
DECLARE
    next_user_id bigint;
BEGIN
    IF (SELECT count(*) FROM demo.users) <> 3
       OR (SELECT count(*) FROM demo.products) <> 3
       OR (SELECT count(*) FROM demo.orders) <> 3
       OR (SELECT stock FROM demo.products WHERE id = 1) IS DISTINCT FROM 10 THEN
        RAISE EXCEPTION 'Unexpected restored data';
    END IF;
    IF (SELECT sum(o.amount) FROM demo.orders AS o
        JOIN demo.users AS u ON u.id = o.user_id WHERE u.username = 'alice')
       IS DISTINCT FROM 140.00 THEN
        RAISE EXCEPTION 'Unexpected order total';
    END IF;

    INSERT INTO demo.users (username, email) VALUES ('restore-check', 'restore@example.test')
    RETURNING id INTO next_user_id;
    IF next_user_id <> 4 THEN
        RAISE EXCEPTION 'Identity sequence was not restored';
    END IF;

    BEGIN
        INSERT INTO demo.orders (user_id, product_id, amount, status, ordered_at)
        VALUES (999, 1, 1, 'paid', CURRENT_TIMESTAMP);
        RAISE EXCEPTION 'Foreign key did not reject the order';
    EXCEPTION WHEN foreign_key_violation THEN
        NULL;
    END;
    BEGIN
        UPDATE demo.products SET stock = -1 WHERE id = 1;
        RAISE EXCEPTION 'CHECK did not reject negative stock';
    EXCEPTION WHEN check_violation THEN
        NULL;
    END;
    BEGIN
        INSERT INTO demo.users (username, email) VALUES ('alice', 'duplicate@example.test');
        RAISE EXCEPTION 'UNIQUE did not reject duplicate username';
    EXCEPTION WHEN unique_violation THEN
        NULL;
    END;
END
$check$;
ROLLBACK;
