# SQL Шпаргалка


---

## Содержание
1. [Основные операции (CRUD)](#основные-операции-crud)
2. [Фильтрация и сортировка](#фильтрация-и-сортировка)
3. [Агрегатные функции](#агрегатные-функции)
4. [Группировка данных](#группировка-данных)
5. [Объединение таблиц (JOIN)](#объединение-таблиц-join)
6. [Подзапросы](#подзапросы)
7. [Модификация данных](#модификация-данных)
8. [Создание и изменение структуры](#создание-и-изменение-структуры)
9. [Индексы](#индексы)
10. [Транзакции](#транзакции)
11. [Оконные функции](#оконные-функции)
12. [CTE (Common Table Expressions)](#cte-common-table-expressions)
13. [Полезные советы](#полезные-советы)
14. [Ресурсы для изучения](#ресурсы-для-изучения)

---

## Основные операции (CRUD)

### Выборка данных (SELECT)
```sql
-- Базовая выборка
SELECT * FROM table_name;

-- Выбор конкретных столбцов
SELECT column1, column2 FROM table_name;

-- Выбор с уникальными значениями
SELECT DISTINCT column FROM table_name;

-- Псевдонимы (алиасы)
SELECT column AS alias_name FROM table_name;
SELECT column alias_name FROM table_name; -- AS можно опустить
```

### Ограничение вывода
```sql
-- Ограничение количества строк (разный синтаксис в СУБД)
-- MySQL, PostgreSQL, SQLite
SELECT * FROM table_name LIMIT 10;

-- SQL Server, MS Access
SELECT TOP 10 * FROM table_name;

-- Oracle
SELECT * FROM table_name WHERE ROWNUM <= 10;

-- Пропуск строк (пагинация)
-- MySQL, PostgreSQL
SELECT * FROM table_name LIMIT 10 OFFSET 20; -- пропустить 20, взять 10

-- Более современный синтаксис (SQL:2008)
SELECT * FROM table_name OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

---

## Фильтрация и сортировка

### Операторы WHERE
```sql
-- Базовые операторы сравнения
SELECT * FROM table_name WHERE column = value;
SELECT * FROM table_name WHERE column > value;
SELECT * FROM table_name WHERE column < value;
SELECT * FROM table_name WHERE column >= value;
SELECT * FROM table_name WHERE column <= value;
SELECT * FROM table_name WHERE column <> value; -- не равно
SELECT * FROM table_name WHERE column != value; -- не равно (альтернатива)

-- Логические операторы
SELECT * FROM table_name 
WHERE condition1 AND condition2;

SELECT * FROM table_name 
WHERE condition1 OR condition2;

SELECT * FROM table_name 
WHERE NOT condition;

-- BETWEEN
SELECT * FROM table_name 
WHERE column BETWEEN value1 AND value2;

-- IN
SELECT * FROM table_name 
WHERE column IN (value1, value2, value3);

-- LIKE (поиск по шаблону)
SELECT * FROM table_name 
WHERE column LIKE 'A%'; -- начинается с A

SELECT * FROM table_name 
WHERE column LIKE '%A%'; -- содержит A

SELECT * FROM table_name 
WHERE column LIKE '_A%'; -- второй символ A

-- IS NULL / IS NOT NULL
SELECT * FROM table_name 
WHERE column IS NULL;

SELECT * FROM table_name 
WHERE column IS NOT NULL;
```

### Сортировка (ORDER BY)
```sql
-- Сортировка по возрастанию (ASC по умолчанию)
SELECT * FROM table_name ORDER BY column ASC;

-- Сортировка по убыванию
SELECT * FROM table_name ORDER BY column DESC;

-- Сортировка по нескольким столбцам
SELECT * FROM table_name 
ORDER BY column1 DESC, column2 ASC;

-- Сортировка по номеру столбца (не рекомендуется для production)
SELECT column1, column2 FROM table_name ORDER BY 1, 2;
```

---

## Агрегатные функции

```sql
-- COUNT - подсчет строк
SELECT COUNT(*) FROM table_name;
SELECT COUNT(column) FROM table_name; -- игнорирует NULL
SELECT COUNT(DISTINCT column) FROM table_name;

-- SUM - сумма
SELECT SUM(column) FROM table_name;

-- AVG - среднее значение
SELECT AVG(column) FROM table_name;

-- MIN/MAX - минимальное/максимальное значение
SELECT MIN(column), MAX(column) FROM table_name;

-- Статистика в одном запросе
SELECT 
    COUNT(*) as total_rows,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    SUM(price) as total_price
FROM products;
```

---

## Группировка данных

### GROUP BY
```sql
-- Группировка по одному столбцу
SELECT column, COUNT(*)
FROM table_name
GROUP BY column;

-- Группировка по нескольким столбцам
SELECT column1, column2, COUNT(*)
FROM table_name
GROUP BY column1, column2;

-- Группировка с агрегатными функциями
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category;
```

### HAVING (фильтрация групп)
```sql
-- WHERE фильтрует строки, HAVING фильтрует группы
SELECT category, COUNT(*)
FROM products
GROUP BY category
HAVING COUNT(*) > 10;

-- Комбинация WHERE и HAVING
SELECT category, AVG(price)
FROM products
WHERE price > 0
GROUP BY category
HAVING AVG(price) > 100;
```

---

## Объединение таблиц (JOIN)

### Типы JOIN
```sql
-- INNER JOIN (пересечение)
SELECT *
FROM table1
INNER JOIN table2 ON table1.id = table2.table1_id;

-- LEFT JOIN (все из левой таблицы + совпадения из правой)
SELECT *
FROM table1
LEFT JOIN table2 ON table1.id = table2.table1_id;

-- RIGHT JOIN (все из правой таблицы + совпадения из левой)
SELECT *
FROM table1
RIGHT JOIN table2 ON table1.id = table2.table1_id;

-- FULL OUTER JOIN (все строки из обеих таблиц)
SELECT *
FROM table1
FULL OUTER JOIN table2 ON table1.id = table2.table1_id;

-- CROSS JOIN (декартово произведение)
SELECT * FROM table1 CROSS JOIN table2;

-- SELF JOIN (объединение таблицы с собой)
SELECT e.name, m.name as manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

### Практические примеры JOIN
```sql
-- JOIN с несколькими условиями
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN products p ON o.product_id = p.id
WHERE o.status = 'completed';

-- Использование USING при совпадении имен столбцов
SELECT *
FROM table1
JOIN table2 USING (id);

-- NATURAL JOIN (автоматическое объединение по одинаковым именам столбцов)
SELECT * FROM table1 NATURAL JOIN table2;
```

---

## Подзапросы

### Подзапросы в WHERE
```sql
-- Сравнение с результатом подзапроса
SELECT * FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- IN с подзапросом
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders WHERE total > 1000);

-- EXISTS
SELECT * FROM suppliers s
WHERE EXISTS (
    SELECT 1 FROM products p 
    WHERE p.supplier_id = s.id AND p.price < 10
);
```

### Подзапросы в SELECT
```sql
SELECT 
    name,
    price,
    (SELECT AVG(price) FROM products) as avg_price,
    price - (SELECT AVG(price) FROM products) as diff_from_avg
FROM products;
```

### Подзапросы в FROM
```sql
SELECT category, avg_price
FROM (
    SELECT category, AVG(price) as avg_price
    FROM products
    GROUP BY category
) as category_stats
WHERE avg_price > 50;
```

---

## Модификация данных

### INSERT
```sql
-- Вставка одной строки
INSERT INTO table_name (column1, column2)
VALUES (value1, value2);

-- Вставка нескольких строк
INSERT INTO table_name (column1, column2)
VALUES 
    (value1a, value2a),
    (value1b, value2b),
    (value1c, value2c);

-- Вставка из результата SELECT
INSERT INTO table_name (column1, column2)
SELECT column1, column2 FROM other_table WHERE condition;

-- INSERT с RETURNING (PostgreSQL, SQL Server - OUTPUT)
INSERT INTO table_name (name) VALUES ('John') RETURNING id;
```

### UPDATE
```sql
-- Обновление всех строк
UPDATE table_name SET column = value;

-- Обновление с условием
UPDATE table_name 
SET column1 = value1, column2 = value2
WHERE condition;

-- Обновление с JOIN (пример для MySQL)
UPDATE products p
JOIN categories c ON p.category_id = c.id
SET p.price = p.price * 1.1
WHERE c.name = 'Electronics';

-- UPDATE с RETURNING (PostgreSQL)
UPDATE products SET price = price * 1.1 WHERE id = 1 RETURNING *;
```

### DELETE
```sql
-- Удаление всех строк (осторожно!)
DELETE FROM table_name;

-- Удаление с условием
DELETE FROM table_name WHERE condition;

-- Каскадное удаление (зависит от настроек БД)
DELETE FROM customers WHERE id = 1;
-- Удалит связанные заказы, если настроены каскадные ограничения

-- TRUNCATE (быстрее чем DELETE, нельзя откатить в некоторых БД)
TRUNCATE TABLE table_name;
```

---

## Создание и изменение структуры

### CREATE TABLE
```sql
-- Базовая таблица
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- С внешним ключом
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,
    total DECIMAL(10, 2),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- С проверкой (CHECK constraint)
CREATE TABLE products (
    id INT PRIMARY KEY,
    price DECIMAL(10, 2) CHECK (price >= 0),
    quantity INT CHECK (quantity >= 0)
);
```

### ALTER TABLE
```sql
-- Добавление столбца
ALTER TABLE table_name ADD column_name datatype;

-- Удаление столбца
ALTER TABLE table_name DROP COLUMN column_name;

-- Изменение типа столбца
ALTER TABLE table_name MODIFY column_name new_datatype;

-- Переименование столбца
ALTER TABLE table_name RENAME COLUMN old_name TO new_name;

-- Добавление ограничения
ALTER TABLE table_name ADD CONSTRAINT constraint_name PRIMARY KEY (column);
ALTER TABLE table_name ADD FOREIGN KEY (column) REFERENCES other_table(column);
ALTER TABLE table_name ADD UNIQUE (column);

-- Удаление ограничения
ALTER TABLE table_name DROP CONSTRAINT constraint_name;
```

### DROP TABLE
```sql
-- Удаление таблицы
DROP TABLE table_name;

-- Удаление с проверкой существования
DROP TABLE IF EXISTS table_name;

-- Удаление с каскадом (зависимые объекты тоже удаляются)
DROP TABLE table_name CASCADE;
```

---

## Индексы

### Создание индексов
```sql
-- Простой индекс
CREATE INDEX idx_column ON table_name (column);

-- Уникальный индекс
CREATE UNIQUE INDEX idx_unique_column ON table_name (column);

-- Составной индекс
CREATE INDEX idx_multi ON table_name (column1, column2);

-- Индекс с указанием порядка сортировки
CREATE INDEX idx_desc ON table_name (column DESC);

-- Частичный индекс (PostgreSQL)
CREATE INDEX idx_partial ON table_name (column) WHERE condition;

-- Полнотекстовый индекс (MySQL)
CREATE FULLTEXT INDEX idx_ft ON table_name (text_column);
```

### Управление индексами
```sql
-- Просмотр индексов
SHOW INDEX FROM table_name; -- MySQL
SELECT * FROM pg_indexes WHERE tablename = 'table_name'; -- PostgreSQL

-- Удаление индекса
DROP INDEX index_name ON table_name; -- MySQL
DROP INDEX index_name; -- PostgreSQL, SQL Server

-- Перестроение индекса (SQL Server)
ALTER INDEX index_name ON table_name REBUILD;

-- Анализ использования индекса (PostgreSQL)
EXPLAIN ANALYZE SELECT * FROM table_name WHERE column = value;
```

---

## Транзакции

```sql
-- Начало транзакции
BEGIN TRANSACTION; -- или START TRANSACTION;

-- Работа в транзакции
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Подтверждение транзакции
COMMIT;

-- Откат транзакции
ROLLBACK;

-- Точки сохранения
BEGIN TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
SAVEPOINT after_first_update;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- Если что-то пошло не так
ROLLBACK TO SAVEPOINT after_first_update;
COMMIT;
```

### Уровни изоляции (на примере PostgreSQL)
```sql
-- Установка уровня изоляции
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Уровни изоляции:
-- READ UNCOMMITTED (грязные чтения возможны)
-- READ COMMITTED (по умолчанию в большинстве БД)
-- REPEATABLE READ (неповторяющиеся чтения предотвращены)
-- SERIALIZABLE (полная изоляция)
```

---

## Оконные функции

### Базовые оконные функции
```sql
-- ROW_NUMBER - порядковый номер строки
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
    salary,
    RANK() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank
FROM employees;

-- Нумерация внутри групп
SELECT 
    department_id,
    name,
    salary,
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_rank
FROM employees;
```

### Агрегатные функции как оконные
```sql
-- Сумма нарастающим итогом
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) as running_total
FROM sales;

-- Среднее по группе
SELECT 
    department_id,
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department_id) as avg_dept_salary
FROM employees;

-- Отношение к общему
SELECT 
    category,
    product,
    sales,
    sales / SUM(sales) OVER () as percent_of_total
FROM product_sales;
```

### Функции смещения
```sql
-- LAG и LEAD (предыдущее/следующее значение)
SELECT 
    date,
    sales,
    LAG(sales) OVER (ORDER BY date) as prev_day_sales,
    LEAD(sales) OVER (ORDER BY date) as next_day_sales
FROM daily_sales;

-- FIRST_VALUE и LAST_VALUE
SELECT 
    department_id,
    name,
    salary,
    FIRST_VALUE(name) OVER (
        PARTITION BY department_id 
        ORDER BY salary DESC
    ) as highest_paid
FROM employees;
```

---

## CTE (Common Table Expressions)

### Простые CTE
```sql
WITH department_stats AS (
    SELECT 
        department_id,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT 
    d.name,
    ds.employee_count,
    ds.avg_salary
FROM departments d
JOIN department_stats ds ON d.id = ds.department_id;
```

### Рекурсивные CTE
```sql
-- Иерархические данные (например, менеджеры и подчиненные)
WITH RECURSIVE employee_hierarchy AS (
    -- Начальная часть: верхний уровень иерархии
    SELECT 
        id,
        name,
        manager_id,
        1 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Рекурсивная часть
    SELECT 
        e.id,
        e.name,
        e.manager_id,
        eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy ORDER BY level, id;
```

---

## Полезные советы

### Производительность
1. **Используйте индексы** для часто фильтруемых и соединяемых столбцов
2. **Избегайте SELECT *** - выбирайте только нужные столбцы
3. **LIMIT/OFFSET** для пагинации, но помните о производительности при больших смещениях
4. **EXPLAIN/EXPLAIN ANALYZE** - ваш лучший друг для анализа запросов
5. **Обновляйте статистику** таблиц для оптимальных планов запросов

### Безопасность
1. **Всегда используйте параметризованные запросы** для предотвращения SQL-инъекций
2. **Минимальные привилегии** - давайте пользователям только необходимые права
3. **Хэшируйте пароли** - никогда не храните пароли в открытом виде
4. **Регулярно делайте бэкапы** важных данных

### Читаемость кода
1. **Используйте псевдонимы** для длинных имен таблиц
2. **Форматируйте SQL** - отступы и переносы строк улучшают читаемость
3. **Комментируйте сложную логику**
4. **Следуйте соглашениям об именовании** в вашей команде/проекте

---

## Ресурсы для изучения

### Документация
- **[MySQL Documentation](https://dev.mysql.com/doc/)** - официальная документация MySQL
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/)** - документация PostgreSQL
- **[SQLite Documentation](https://sqlite.org/docs.html)** - документация SQLite
- **[Microsoft SQL Server Docs](https://docs.microsoft.com/sql/)** - документация SQL Server

### Интерактивные курсы
- **[SQLBolt](https://sqlbolt.com/)** - интерактивные уроки SQL
- **[Mode Analytics SQL Tutorial](https://mode.com/sql-tutorial/)** - SQL для анализа данных
- **[SQLZoo](https://sqlzoo.net/)** - практические упражнения
- **[LeetCode SQL](https://leetcode.com/problemset/database/)** - задачи на SQL

### Книги
- **"Learning SQL"** by Alan Beaulieu
- **"SQL Performance Explained"** by Markus Winand
- **"SQL Cookbook"** by Anthony Molinaro

---

## Примечание
*Составлено с учетом актуальных стандартов SQL на 13.01.2026*
