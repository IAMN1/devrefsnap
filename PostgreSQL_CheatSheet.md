# 🐘 PostgreSQL Шпаргалка

## Содержание
- [Установка и Запуск](#установка-и-запуск)
- [Подключение к СУБД](#подключение-к-субд)
- [Управление Базами Данных](#управление-базами-данных)
- [Управление Таблицами](#управление-таблицами)
- [Типы Данных](#типы-данных)
- [CRUD Операции](#crud-операции)
- [Индексы](#индексы)
- [Оконные Функции](#оконные-функции)
- [Транзакции](#транзакции)
- [Пользователи и Права](#пользователи-и-права)
- [Резервное Копирование](#резервное-копирование)
- [Мониторинг и Оптимизация](#мониторинг-и-оптимизация)
- [Полезные Функции](#полезные-функции)
- [Расширения (Extensions)](#расширения-extensions)

---

## Установка и Запуск

### Ubuntu/Debian
```bash
# Установка PostgreSQL 16
sudo apt update
sudo apt install postgresql-16 postgresql-contrib-16

# Статус службы
sudo systemctl status postgresql

# Запуск/остановка
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql
```

### Docker
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -e POSTGRES_USER=myuser \
  -e POSTGRES_DB=mydatabase \
  -p 5432:5432 \
  postgres:16

# С Docker Compose
version: '3.8'
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: mydatabase
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
volumes:
  postgres_data:
```

---

## Подключение к СУБД

### Командная строка
```bash
# Подключение от имени postgres
sudo -u postgres psql

# Подключение к конкретной базе
psql -U username -d database -h host -p port

# Параметры подключения
psql "postgresql://username:password@host:port/database"

# Выход из psql
\q
```

### Внутри psql
```sql
-- Показать версию PostgreSQL
SELECT version();

-- Показать все базы данных
\l

-- Показать все таблицы текущей базы
\dt

-- Подробная информация о таблице
\d table_name

-- Смена базы данных
\c database_name

-- Показать все схемы
\dn

-- Показать все расширения
\dx
```

---

## Управление Базами Данных

```sql
-- Создать базу данных
CREATE DATABASE database_name
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8'
    TEMPLATE template0;

-- Создать базу с параметрами
CREATE DATABASE mydb WITH 
    OWNER = username
    ENCODING = 'UTF8'
    CONNECTION LIMIT = 100;

-- Удалить базу данных
DROP DATABASE database_name;

-- Переименовать базу
ALTER DATABASE old_name RENAME TO new_name;

-- Изменить владельца
ALTER DATABASE database_name OWNER TO new_owner;

-- Копировать базу данных
CREATE DATABASE newdb TEMPLATE originaldb;

-- Показать размер базы
SELECT pg_size_pretty(pg_database_size('database_name'));

-- Показать все подключения к базе
SELECT * FROM pg_stat_activity WHERE datname = 'database_name';
```

---

## Управление Таблицами

### Создание таблиц
```sql
-- Простая таблица
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Таблица с внешним ключом
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица с наследованием (Partitioning)
CREATE TABLE measurements (
    city_id INT NOT NULL,
    logdate DATE NOT NULL,
    peaktemp INT,
    unitsales INT
) PARTITION BY RANGE (logdate);

-- Создание партиций
CREATE TABLE measurements_y2025m01 PARTITION OF measurements
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- Создание индекса при создании таблицы
CREATE TABLE products (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2),
    category_id INT
) WITH (fillfactor = 70);
```

### Изменение таблиц
```sql
-- Добавить колонку
ALTER TABLE table_name ADD COLUMN column_name data_type;

-- Удалить колонку
ALTER TABLE table_name DROP COLUMN column_name;

-- Изменить тип данных
ALTER TABLE table_name ALTER COLUMN column_name TYPE new_data_type;

-- Добавить ограничение
ALTER TABLE table_name ADD CONSTRAINT constraint_name CHECK (column_name > 0);

-- Удалить ограничение
ALTER TABLE table_name DROP CONSTRAINT constraint_name;

-- Переименовать таблицу
ALTER TABLE old_name RENAME TO new_name;

-- Добавить внешний ключ
ALTER TABLE orders ADD CONSTRAINT fk_user
    FOREIGN KEY (user_id) REFERENCES users(id);

-- Установить значение по умолчанию
ALTER TABLE table_name ALTER COLUMN column_name SET DEFAULT value;

-- Изменить владельца таблицы
ALTER TABLE table_name OWNER TO new_owner;
```

### Управление схемами
```sql
-- Создать схему
CREATE SCHEMA schema_name AUTHORIZATION user_name;

-- Установить путь поиска
SET search_path TO schema_name, public;

-- Перенести таблицу в другую схему
ALTER TABLE table_name SET SCHEMA new_schema;

-- Удалить схему
DROP SCHEMA schema_name CASCADE;
```

---

## Типы Данных

### Числовые типы
```sql
-- Целые числа
SMALLINT     -- 2 байта, -32768 to 32767
INTEGER      -- 4 байта, -2147483648 to 2147483647
BIGINT       -- 8 байт, -9223372036854775808 to 9223372036854775807

-- Автоинкремент
SERIAL       -- INTEGER с автоинкрементом (1 to 2147483647)
BIGSERIAL    -- BIGINT с автоинкрементом

-- Числа с плавающей точкой
REAL         -- 4 байта, 6 десятичных цифр точности
DOUBLE PRECISION  -- 8 байт, 15 десятичных цифр точности

-- Точные числовые
DECIMAL(10, 2)   -- точный числовой тип
NUMERIC(10, 2)   -- синоним DECIMAL
```

### Строковые типы
```sql
VARCHAR(n)   -- строка переменной длины с ограничением
CHAR(n)      -- строка фиксированной длины
TEXT         -- строка неограниченной длины
BYTEA        -- бинарные данные
```

### Дата и время
```sql
DATE         -- дата (2025-01-13)
TIME         -- время (14:30:00)
TIMESTAMP    -- дата и время (2025-01-13 14:30:00)
TIMESTAMPTZ  -- дата и время с часовым поясом
INTERVAL     -- интервал времени
```

### Специальные типы
```sql
-- Массивы
INT[]        -- массив целых чисел
TEXT[][]     -- многомерный массив текста

-- JSON
JSON         -- текстовый JSON
JSONB        -- бинарный JSON (рекомендуется)

-- UUID
UUID         -- универсальный уникальный идентификатор

-- Геометрические
POINT, LINE, LSEG, BOX, PATH, POLYGON, CIRCLE

-- Сетевые
INET, CIDR, MACADDR

-- Битовые
BIT(n), BIT VARYING(n)

-- Перечисления
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');
```

---

## CRUD Операции

### SELECT
```sql
-- Базовый SELECT
SELECT * FROM table_name;

-- Выбор конкретных колонок
SELECT column1, column2 FROM table_name;

-- С условием WHERE
SELECT * FROM users WHERE age > 18 AND is_active = TRUE;

-- Сортировка
SELECT * FROM products ORDER BY price DESC, name ASC;

-- Ограничение количества строк
SELECT * FROM logs LIMIT 100;

-- Пропуск строк
SELECT * FROM logs OFFSET 50 LIMIT 25;

-- Уникальные значения
SELECT DISTINCT category FROM products;

-- Псевдонимы (алиасы)
SELECT 
    u.username AS "Имя пользователя",
    u.email AS "Электронная почта"
FROM users u;

-- Группировка
SELECT 
    department_id,
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5;

-- Подзапросы
SELECT name FROM products 
WHERE price > (SELECT AVG(price) FROM products);

-- JOIN операции
SELECT 
    o.id,
    o.amount,
    u.username
FROM orders o
INNER JOIN users u ON o.user_id = u.id;

-- Типы JOIN:
-- INNER JOIN: только совпадающие строки
-- LEFT JOIN: все строки из левой таблицы
-- RIGHT JOIN: все строки из правой таблицы
-- FULL OUTER JOIN: все строки из обеих таблиц
-- CROSS JOIN: декартово произведение

-- UNION
SELECT name FROM active_users
UNION
SELECT name FROM inactive_users;

-- INTERSECT и EXCEPT
SELECT id FROM table1
INTERSECT
SELECT id FROM table2;
```

### INSERT
```sql
-- Вставка одной строки
INSERT INTO users (username, email) 
VALUES ('john_doe', 'john@example.com');

-- Вставка нескольких строк
INSERT INTO users (username, email) VALUES
('user1', 'user1@example.com'),
('user2', 'user2@example.com'),
('user3', 'user3@example.com');

-- Вставка с RETURNING
INSERT INTO products (name, price) 
VALUES ('Laptop', 999.99)
RETURNING id;

-- Вставка из SELECT
INSERT INTO archived_orders 
SELECT * FROM orders 
WHERE created_at < '2024-01-01';

-- Вставка с ON CONFLICT (UPSERT)
INSERT INTO users (id, username, email) 
VALUES (1, 'john', 'john@example.com')
ON CONFLICT (id) 
DO UPDATE SET 
    username = EXCLUDED.username,
    email = EXCLUDED.email;
```

### UPDATE
```sql
-- Обновление всех строк
UPDATE products SET price = price * 1.1;

-- Обновление с условием
UPDATE users SET is_active = FALSE 
WHERE last_login < NOW() - INTERVAL '1 year';

-- Обновление нескольких колонок
UPDATE employees SET 
    salary = salary * 1.05,
    last_raise = CURRENT_DATE
WHERE performance_rating > 4;

-- Обновление с JOIN
UPDATE orders o
SET status = 'shipped'
FROM users u
WHERE o.user_id = u.id 
  AND u.country = 'USA';

-- Обновление с RETURNING
UPDATE products 
SET stock = stock - 1
WHERE id = 123
RETURNING stock;
```

### DELETE
```sql
-- Удаление всех строк (опасно!)
DELETE FROM table_name;

-- Удаление с условием
DELETE FROM logs 
WHERE created_at < NOW() - INTERVAL '6 months';

-- Удаление с использованием подзапроса
DELETE FROM products 
WHERE category_id IN (
    SELECT id FROM categories 
    WHERE is_active = FALSE
);

-- Быстрое удаление всех строк (без журналирования)
TRUNCATE TABLE table_name;

-- TRUNCATE с CASCADE
TRUNCATE TABLE parent_table CASCADE;
```

---

## Индексы

### Создание индексов
```sql
-- Базовый индекс
CREATE INDEX idx_users_email ON users(email);

-- Уникальный индекс
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Составной индекс
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Частичный индекс
CREATE INDEX idx_active_users ON users(email) 
WHERE is_active = TRUE;

-- Индекс для полнотекстового поиска
CREATE INDEX idx_products_description ON products 
USING GIN (to_tsvector('english', description));

-- Индекс по выражению
CREATE INDEX idx_users_lower_username ON users(LOWER(username));

-- Индекс для LIKE с префиксом
CREATE INDEX idx_users_username_pattern ON users(username varchar_pattern_ops);
```

### Типы индексов
```sql
-- B-tree (по умолчанию) - для сравнений и сортировок
CREATE INDEX idx_name ON table(column);

-- Hash - для точных совпадений (=)
CREATE INDEX idx_name ON table USING HASH(column);

-- GiST - для геоданных, полнотекстового поиска
CREATE INDEX idx_name ON table USING GIST(column);

-- GIN - для массивов, JSON, полнотекстового поиска
CREATE INDEX idx_name ON table USING GIN(column);

-- SP-GiST - для кластеризованных данных
CREATE INDEX idx_name ON table USING SPGIST(column);

-- BRIN - для больших таблиц с естественной сортировкой
CREATE INDEX idx_name ON table USING BRIN(column);
```

### Управление индексами
```sql
-- Перестроение индекса
REINDEX INDEX index_name;
REINDEX TABLE table_name;

-- Параллельное создание индекса
CREATE INDEX CONCURRENTLY idx_name ON table(column);

-- Анализ использования индексов
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Показать все индексы таблицы
\di table_name

-- Удалить индекс
DROP INDEX index_name;

-- Переименовать индекс
ALTER INDEX old_name RENAME TO new_name;
```

---

## Оконные Функции

### Базовые оконные функции
```sql
-- ROW_NUMBER
SELECT 
    id,
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as rank
FROM employees;

-- RANK и DENSE_RANK
SELECT 
    id,
    name,
    score,
    RANK() OVER (ORDER BY score DESC) as rank,
    DENSE_RANK() OVER (ORDER BY score DESC) as dense_rank
FROM students;

-- Накопительная сумма
SELECT 
    date,
    revenue,
    SUM(revenue) OVER (ORDER BY date) as cumulative_revenue
FROM sales;

-- Скользящее среднее
SELECT 
    date,
    temperature,
    AVG(temperature) OVER (
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) as moving_avg
FROM measurements;
```

### PARTITION BY
```sql
-- Ранжирование внутри групп
SELECT 
    department_id,
    employee_name,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department_id 
        ORDER BY salary DESC
    ) as dept_rank
FROM employees;

-- Сравнение с средним по отделу
SELECT 
    department_id,
    employee_name,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) as dept_avg_salary
FROM employees;

-- LAG и LEAD
SELECT 
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) as prev_day_revenue,
    LEAD(revenue) OVER (ORDER BY date) as next_day_revenue
FROM daily_sales;
```

### Фреймы окон
```sql
-- Три варианта определения фрейма
ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
RANGE BETWEEN INTERVAL '7 days' PRECEDING AND CURRENT ROW
GROUPS BETWEEN 1 PRECEDING AND 1 FOLLOWING

-- Примеры использования
SELECT 
    date,
    SUM(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as weekly_sum
FROM transactions;
```

---

## Транзакции

### Управление транзакциями
```sql
-- Начало транзакции
BEGIN;
-- или
START TRANSACTION;

-- Фиксация изменений
COMMIT;

-- Откат изменений
ROLLBACK;

-- Транзакция с точкой сохранения
BEGIN;
INSERT INTO table1 VALUES (1);
SAVEPOINT my_savepoint;
INSERT INTO table2 VALUES (2);
-- Если что-то пошло не так
ROLLBACK TO SAVEPOINT my_savepoint;
-- Продолжаем работу
INSERT INTO table2 VALUES (3);
COMMIT;
```

### Уровни изоляции
```sql
-- Установка уровня изоляции
SET TRANSACTION ISOLATION LEVEL level;

-- Уровни изоляции:
-- READ UNCOMMITTED (в PostgreSQL работает как READ COMMITTED)
-- READ COMMITTED (по умолчанию)
-- REPEATABLE READ
-- SERIALIZABLE

-- Пример использования
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- операции
COMMIT;
```

### Блокировки
```sql
-- Блокировка строк
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- Блокировка для чтения
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- Блокировка таблицы
LOCK TABLE table_name IN EXCLUSIVE MODE;

-- Режимы блокировки таблиц:
-- ACCESS SHARE - SELECT
-- ROW SHARE - SELECT FOR UPDATE/FOR SHARE
-- ROW EXCLUSIVE - INSERT, UPDATE, DELETE
-- SHARE UPDATE EXCLUSIVE - VACUUM, CREATE INDEX CONCURRENTLY
-- SHARE - CREATE INDEX
-- SHARE ROW EXCLUSIVE
-- EXCLUSIVE
-- ACCESS EXCLUSIVE - DROP TABLE, TRUNCATE, ALTER TABLE
```

---

## Пользователи и Права

### Управление пользователями и ролями
```sql
-- Создать пользователя
CREATE USER username WITH PASSWORD 'password';

-- Создать роль
CREATE ROLE role_name;

-- Удалить пользователя
DROP USER username;

-- Изменить пароль
ALTER USER username WITH PASSWORD 'new_password';

-- Создать пользователя с привилегиями
CREATE USER admin WITH 
    PASSWORD 'secret'
    CREATEDB
    CREATEROLE
    LOGIN
    VALID UNTIL '2026-12-31';

-- Дать привилегии на базу данных
GRANT CONNECT ON DATABASE dbname TO username;

-- Дать все привилегии на схему
GRANT ALL PRIVILEGES ON SCHEMA schema_name TO username;

-- Дать привилегии на таблицу
GRANT SELECT, INSERT, UPDATE ON table_name TO username;
GRANT ALL PRIVILEGES ON table_name TO username;

-- Дать привилегии на все таблицы в схеме
GRANT SELECT ON ALL TABLES IN SCHEMA public TO username;

-- Дать привилегии на выполнение функций
GRANT EXECUTE ON FUNCTION function_name TO username;

-- Отозвать привилегии
REVOKE INSERT ON table_name FROM username;

-- Наследование ролей
GRANT role_name TO username;

-- Показать привилегии
\du  -- список пользователей/ролей
\dp  -- привилегии таблиц
\dn+ -- привилегии схем
```

### Безопасность и аутентификация
```sql
-- Изменить pg_hba.conf
# TYPE  DATABASE  USER  ADDRESS  METHOD
host    all       all   0.0.0.0/0  md5
local   all       all             peer

-- SSL соединения
hostssl all       all   0.0.0.0/0  md5

-- Проверить SSL
SHOW ssl;
SELECT * FROM pg_stat_ssl;
```

---

## Резервное Копирование

### pg_dump и pg_restore
```bash
# Дамп одной базы
pg_dump -U username -d database_name -f backup.sql

# Дамп в сжатом формате
pg_dump -U username -d database_name -F c -f backup.dump

# Дамп только схемы
pg_dump -U username -d database_name -s -f schema.sql

# Дамп только данных
pg_dump -U username -d database_name -a -f data.sql

# Дамп определенных таблиц
pg_dump -U username -d database_name -t table1 -t table2 -f tables.sql

# Дамп всех баз
pg_dumpall -U username -f alldb.sql

# Восстановление из SQL файла
psql -U username -d database_name -f backup.sql

# Восстановление из custom формата
pg_restore -U username -d database_name backup.dump

# Восстановление с параллельной обработкой
pg_restore -U username -d database_name -j 4 backup.dump

# Вывести список объектов в дампе
pg_restore -l backup.dump > list.txt
```

### Репликация и PITR
```sql
-- Настройка репликации
-- В postgresql.conf:
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10

-- Создание слота репликации
SELECT * FROM pg_create_physical_replication_slot('replica_slot');

-- Базовый backup
pg_basebackup -D /path/to/backup -Ft -z -P

-- Точка во времени восстановление (PITR)
-- В postgresql.conf:
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'

-- Восстановление на определенное время
-- В recovery.conf или postgresql.auto.conf:
restore_command = 'cp /path/to/archive/%f %p'
recovery_target_time = '2025-01-13 14:30:00'
```

---

## Мониторинг и Оптимизация

### Системные представления
```sql
-- Активные запросы
SELECT * FROM pg_stat_activity;

-- Статистика по таблицам
SELECT * FROM pg_stat_user_tables;

-- Статистика по индексам
SELECT * FROM pg_stat_user_indexes;

-- Размеры таблиц и индексов
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as total_size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;

-- Блокировки
SELECT * FROM pg_locks;

-- Дисковый ввод/вывод
SELECT * FROM pg_statio_user_tables;

-- Долгие запросы
SELECT 
    pid,
    now() - query_start as duration,
    query,
    state
FROM pg_stat_activity 
WHERE state != 'idle' 
ORDER BY duration DESC;
```

### Оптимизация запросов
```sql
-- EXPLAIN команда
EXPLAIN SELECT * FROM users WHERE id = 1;

-- EXPLAIN с анализом выполнения
EXPLAIN ANALYZE SELECT * FROM users WHERE email LIKE 'test%@example.com';

-- Статистика выполнения
SELECT * FROM pg_stat_statements;

-- Включение pg_stat_statements
-- В postgresql.conf:
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

-- Очистка статистики
SELECT pg_stat_statements_reset();

-- Настройка планировщика
SET enable_seqscan = off;
SET random_page_cost = 1.1;
SET effective_cache_size = '4GB';

-- Сбор статистики
ANALYZE table_name;
VACUUM ANALYZE table_name;
```

### Поддержание базы данных
```sql
-- Очистка (VACUUM)
VACUUM table_name;          -- обычный VACUUM
VACUUM FULL table_name;     -- полная перезапись
VACUUM ANALYZE table_name;  -- VACUUM + обновление статистики

-- Автоочистка
-- В postgresql.conf:
autovacuum = on
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50

-- Перестроение индексов
REINDEX TABLE table_name;
REINDEX DATABASE database_name;

-- Проверка целостности
CHECKPOINT;
SELECT * FROM pg_stat_database;
```

---

## Полезные Функции

### Строковые функции
```sql
-- Конкатенация
SELECT CONCAT(first_name, ' ', last_name) as full_name;
SELECT first_name || ' ' || last_name as full_name;

-- Преобразование регистра
SELECT UPPER(name), LOWER(email), INITCAP(title);

-- Подстроки
SELECT SUBSTRING('PostgreSQL' FROM 1 FOR 4); -- 'Post'
SELECT LEFT('PostgreSQL', 4);  -- 'Post'
SELECT RIGHT('PostgreSQL', 6); -- 'greSQL'

-- Поиск и замена
SELECT POSITION('SQL' IN 'PostgreSQL'); -- 5
SELECT REPLACE('Hello World', 'World', 'PostgreSQL');
SELECT OVERLAY('PostXXXX' PLACING 'greSQL' FROM 5);

-- Триммирование
SELECT TRIM('  Hello  ');
SELECT TRIM(LEADING '0' FROM '000123');
SELECT LTRIM('  Hello'), RTRIM('Hello  ');

-- Разделение строк
SELECT UNNEST(STRING_TO_ARRAY('a,b,c', ','));

-- Форматирование
SELECT FORMAT('Hello %s, your balance is %s', name, balance);
```

### Функции даты и времени
```sql
-- Текущая дата и время
SELECT CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP;
SELECT NOW(), LOCALTIMESTAMP;

-- Извлечение компонентов
SELECT 
    EXTRACT(YEAR FROM date_column),
    EXTRACT(MONTH FROM date_column),
    EXTRACT(DAY FROM date_column),
    EXTRACT(HOUR FROM timestamp_column),
    EXTRACT(DOW FROM date_column) -- день недели (0-6)

-- Интервалы
SELECT NOW() - INTERVAL '1 day';
SELECT NOW() + INTERVAL '2 hours 30 minutes';
SELECT AGE('2025-01-13', '2020-01-01'); -- 5 years 12 days

-- Форматирование даты
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS');
SELECT TO_CHAR(NOW(), 'Day, DD Month YYYY');

-- Преобразование строки в дату
SELECT TO_DATE('2025-01-13', 'YYYY-MM-DD');
SELECT TO_TIMESTAMP('2025-01-13 14:30:00', 'YYYY-MM-DD HH24:MI:SS');

-- Округление даты
SELECT DATE_TRUNC('month', NOW()); -- первое число месяца
SELECT DATE_TRUNC('hour', NOW());  -- начало часа
```

### Математические функции
```sql
-- Округление
SELECT ROUND(123.456, 2);  -- 123.46
SELECT CEIL(123.456);      -- 124
SELECT FLOOR(123.456);     -- 123
SELECT TRUNC(123.456, 2);  -- 123.45

-- Абсолютное значение и знак
SELECT ABS(-123), SIGN(-123), SIGN(123), SIGN(0);

-- Степени и корни
SELECT POWER(2, 3), SQRT(16), CBRT(27), EXP(1);

-- Логарифмы
SELECT LN(2.71828), LOG(10, 100), LOG10(1000);

-- Тригонометрия
SELECT SIN(PI()), COS(PI()), TAN(PI()), PI();

-- Случайные числа
SELECT RANDOM();           -- от 0 до 1
SELECT FLOOR(RANDOM() * 100 + 1); -- от 1 до 100

-- Остаток от деления
SELECT MOD(10, 3);  -- 1
```

### JSON функции
```sql
-- Создание JSON
SELECT JSON_BUILD_OBJECT('name', 'John', 'age', 30);
SELECT JSON_AGG(row_to_json(t)) FROM (SELECT id, name FROM users) t;

-- Доступ к JSON
SELECT json_column->>'name' FROM table;          -- текст
SELECT json_column->'address'->>'city' FROM table; -- вложенный

-- Проверки
SELECT json_column ? 'name' FROM table;  -- содержит ключ
SELECT json_typeof(json_column->'age') FROM table;

-- Обновление JSONB
UPDATE table SET json_column = json_column || '{"active": true}';

-- Поиск в JSONB
SELECT * FROM table WHERE json_column @> '{"active": true}';
SELECT * FROM table WHERE json_column -> 'tags' ? 'postgresql';

-- Агрегация в JSON
SELECT JSON_OBJECT_AGG(name, value) FROM settings;
```

### Условные выражения
```sql
-- CASE выражение
SELECT 
    name,
    CASE 
        WHEN age < 18 THEN 'minor'
        WHEN age < 65 THEN 'adult'
        ELSE 'senior'
    END as age_group
FROM users;

-- COALESCE (первое не NULL значение)
SELECT COALESCE(middle_name, '') FROM users;

-- NULLIF (возвращает NULL если значения равны)
SELECT NULLIF(column, '') FROM table;

-- GREATEST и LEAST
SELECT GREATEST(1, 2, 3), LEAST(1, 2, 3);
```

---

## Расширения (Extensions)

### Популярные расширения
```sql
-- Установить расширение
CREATE EXTENSION extension_name;

-- Установить из определенной схемы
CREATE EXTENSION extension_name SCHEMA schema_name;

-- Удалить расширение
DROP EXTENSION extension_name;

-- Показать доступные расширения
SELECT * FROM pg_available_extensions;

-- Показать установленные расширения
SELECT * FROM pg_extension;
```

### Полезные расширения
```sql
-- Для полнотекстового поиска
CREATE EXTENSION unaccent;
CREATE EXTENSION pg_trgm;  -- триграммы для поиска

-- Для UUID
CREATE EXTENSION "uuid-ossp";

-- Для статистики запросов
CREATE EXTENSION pg_stat_statements;

-- Для пространственных данных
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Для сжатия данных
CREATE EXTENSION zstd;

-- Для паролей
CREATE EXTENSION pgcrypto;  -- криптографические функции

-- Для партиционирования
CREATE EXTENSION pg_partman;  -- управление партициями

-- Для репликации
CREATE EXTENSION pglogical;

-- Для отладки
CREATE EXTENSION pldbgapi;  -- отладка PL/pgSQL

-- Для администрирования
CREATE EXTENSION pg_repack;  -- переупаковка таблиц без эксклюзивной блокировки
```

### Использование расширений
```sql
-- Пример с uuid-ossp
SELECT uuid_generate_v4();

-- Пример с pg_trgm (поиск похожих строк)
SELECT * FROM users 
WHERE similarity(username, 'johndoe') > 0.3 
ORDER BY similarity(username, 'johndoe') DESC;

-- Пример с pgcrypto
SELECT crypt('password', gen_salt('bf', 8));
```

---

## Дополнительные Советы

### Производительность
```sql
-- Используйте подготавливаемые запросы
PREPARE user_query (INT) AS 
SELECT * FROM users WHERE id = $1;
EXECUTE user_query(1);

-- Пакетная вставка
BEGIN;
INSERT INTO table VALUES (...);
INSERT INTO table VALUES (...);
COMMIT;

-- Временные таблицы для сложных операций
CREATE TEMPORARY TABLE temp_results AS 
SELECT ...;

-- Материализованные представления для сложных запросов
CREATE MATERIALIZED VIEW sales_summary AS 
SELECT ...;
REFRESH MATERIALIZED VIEW sales_summary;

-- Оптимизация JOIN
-- Используйте INNER JOIN вместо OUTER JOIN если возможно
-- Фильтруйте как можно раньше
-- Используйте коррелированные подзапросы для небольших наборов данных
```

### Безопасность
```sql
-- Используйте параметризованные запросы
-- Вместо: SELECT * FROM users WHERE name = '$name'
-- Используйте: SELECT * FROM users WHERE name = $1

-- Ограничивайте привилегии
-- Не используйте суперпользователя для приложений

-- Шифруйте чувствительные данные
-- Используйте pgcrypto для хранения паролей

-- Регулярно обновляйте PostgreSQL
-- Следите за security advisory
```

### Отладка
```sql
-- Включить логирование
-- В postgresql.conf:
log_statement = 'all'  # или 'mod', 'ddl'
log_duration = on
log_min_duration_statement = 1000  # мс

-- Отладка PL/pgSQL
RAISE NOTICE 'Значение переменной: %', variable;
RAISE EXCEPTION 'Ошибка: %', error_message;

-- Используйте psql команды для отладки
\timing  -- включить время выполнения
\set ECHO all  -- показывать все команды
```

---

## Быстрые Ссылки

### Команды psql
```
\? - помощь по командам psql
\h - помощь по SQL командам
\q - выход
\l - список баз данных
\c - подключиться к базе
\d - описание таблиц
\dt - список таблиц
\di - список индексов
\du - список пользователей
\dn - список схем
\df - список функций
\dv - список представлений
\dx - список расширений
\z - привилегии таблиц
\g или ; - выполнить запрос
\s - история команд
\i - выполнить SQL из файла
\o - вывод в файл
\timing - включить/выключить тайминг
\x - расширенный вывод
```

### Важные файлы конфигурации
```
postgresql.conf - основная конфигурация
pg_hba.conf - конфигурация аутентификации
pg_ident.conf - маппинг пользователей
postgresql.auto.conf - автоматически генерируемые настройки
```

### Полезные представления каталога
```
pg_class - таблицы, индексы, последовательности
pg_namespace - схемы
pg_user, pg_roles - пользователи и роли
pg_database - базы данных
pg_tables - таблицы
pg_indexes - индексы
pg_views - представления
pg_settings - параметры конфигурации
```

---

*Эта шпаргалка охватывает основные аспекты работы с PostgreSQL. Для более подробной информации обращайтесь к [официальной документации](https://www.postgresql.org/docs/current/).*
