# Шпаргалка по SQLite

---

## Содержание
1. [Введение](#введение)
2. [Основные характеристики](#основные-характеристики)
3. [Типы данных SQLite](#типы-данных-sqlite)
4. [Работа через командную строку](#работа-через-командную-строку)
5. [Создание и подключение БД](#создание-и-подключение-бд)
6. [Работа с таблицами](#работа-с-таблицами)
7. [CRUD операции](#crud-операции)
8. [Индексы](#индексы)
9. [Транзакции](#транзакции)
10. [Встроенные функции](#встроенные-функции)
11. [Практические примеры](#практические-примеры)
12. [Полезные ссылки](#полезные-ссылки)

---

## Введение

SQLite — встраиваемая реляционная СУБД, реализованная в виде библиотеки на языке C. Не требует отдельного серверного процесса, хранит данные в одном файле.

## Основные характеристики

- **Zero-configuration** — не требует настройки
- **Serverless** — нет отдельного сервера
- **Single-file database** — вся БД в одном файле
- **Cross-platform** — работает на всех основных ОС
- **Public domain** — полностью открытый код

## Типы данных SQLite

SQLite использует динамическую типизацию (система гибкой типизации):

| Тип | Описание |
|-----|----------|
| `NULL` | Значение NULL |
| `INTEGER` | Целое число (1, 2, 3, 4, 6, или 8 байт) |
| `REAL` | Число с плавающей точкой (8-байтное) |
| `TEXT` | Текстовая строка (кодировка UTF-8, UTF-16BE или UTF-16LE) |
| `BLOB` | Бинарные данные |

*Примечание:* SQLite поддерживает аффинные типы (NUMERIC, BOOLEAN, DATE и др.), которые конвертируются в пять основных типов.

## Работа через командную строку

### Запуск SQLite CLI:
```bash
# Открыть или создать БД
sqlite3 database.db

# Открыть БД в режиме только для чтения
sqlite3 -readonly database.db

# Выполнить SQL-скрипт из файла
sqlite3 database.db < script.sql

# Выполнить команду и выйти
sqlite3 database.db "SELECT * FROM users;"
```

### Основные команды в CLI (точки):
```sql
.help -- Показать все команды
.open filename.db -- Открыть БД
.tables -- Показать все таблицы
.schema [table] -- Показать структуру таблицы
.mode [mode] -- Установить режим вывода (csv, column, json, list, etc.)
.headers on|off -- Показать/скрыть заголовки столбцов
.output filename -- Перенаправить вывод в файл
.import file.csv table -- Импорт CSV в таблицу
.quit -- Выйти из SQLite
```

## Создание и подключение БД

### В разных языках программирования:

**Python:**
```python
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()
```

**Node.js:**
```javascript
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('database.db');
```

**Java:**
```java
import java.sql.*;
Connection conn = DriverManager.getConnection("jdbc:sqlite:database.db");
```

**C#:**
```csharp
using Microsoft.Data.Sqlite;
var connection = new SqliteConnection("Data Source=database.db");
```

## Работа с таблицами

### Создание таблицы:
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    age INTEGER CHECK(age >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

### Удаление таблицы:
```sql
DROP TABLE IF EXISTS users;
```

### Изменение таблицы:
```sql
-- Добавление столбца
ALTER TABLE users ADD COLUMN phone TEXT;

-- Переименование таблицы
ALTER TABLE users RENAME TO clients;

-- Удаление столбца (SQLite 3.35.0+)
ALTER TABLE users DROP COLUMN phone;
```

### Просмотр структуры:
```sql
-- Информация о таблице
PRAGMA table_info(users);

-- Показать SQL создания таблицы
.schema users
```

## CRUD операции

### CREATE (Вставка данных):
```sql
-- Вставка одной строки
INSERT INTO users (username, email, age) 
VALUES ('john_doe', 'john@example.com', 25);

-- Вставка нескольких строк
INSERT INTO users (username, email, age) VALUES
('alice', 'alice@example.com', 30),
('bob', 'bob@example.com', 28);

-- Вставка с возвратом ID
INSERT INTO users (username, email) VALUES ('charlie', 'charlie@example.com');
SELECT last_insert_rowid();
```

### READ (Выборка данных):
```sql
-- Простой SELECT
SELECT * FROM users;

-- Выборка конкретных столбцов
SELECT username, email FROM users;

-- Фильтрация (WHERE)
SELECT * FROM users WHERE age > 25;
SELECT * FROM users WHERE username LIKE 'j%';

-- Сортировка (ORDER BY)
SELECT * FROM users ORDER BY created_at DESC;
SELECT * FROM users ORDER BY age ASC, username DESC;

-- Ограничение результатов (LIMIT/OFFSET)
SELECT * FROM users LIMIT 10;
SELECT * FROM users LIMIT 10 OFFSET 20; -- Пропустить 20, взять 10

-- Группировка (GROUP BY)
SELECT age, COUNT(*) as count FROM users GROUP BY age;
SELECT is_active, AVG(age) as avg_age FROM users GROUP BY is_active;

-- JOIN операции
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount REAL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

SELECT users.username, orders.amount 
FROM users 
INNER JOIN orders ON users.id = orders.user_id;

-- Подзапросы
SELECT username FROM users WHERE id IN (SELECT user_id FROM orders);
```

### UPDATE (Обновление данных):
```sql
-- Обновление всех строк
UPDATE users SET is_active = 0;

-- Обновление с условием
UPDATE users SET age = 26 WHERE username = 'john_doe';

-- Обновление нескольких столбцов
UPDATE users SET age = 27, email = 'new@example.com' WHERE id = 1;

-- Обновление с использованием выражений
UPDATE products SET price = price * 1.1; -- Увеличить цену на 10%
```

### DELETE (Удаление данных):
```sql
-- Удаление всех строк (осторожно!)
DELETE FROM users;

-- Удаление с условием
DELETE FROM users WHERE is_active = 0;

-- Удаление с ограничением
DELETE FROM users WHERE age < 18 LIMIT 10;
```

## Индексы

### Создание индексов:
```sql
-- Простой индекс
CREATE INDEX idx_users_email ON users(email);

-- Уникальный индекс
CREATE UNIQUE INDEX idx_unique_username ON users(username);

-- Составной индекс
CREATE INDEX idx_users_age_active ON users(age, is_active);

-- Частичный индекс (с условием)
CREATE INDEX idx_active_users ON users(username) WHERE is_active = 1;
```

### Управление индексами:
```sql
-- Показать все индексы
SELECT * FROM sqlite_master WHERE type = 'index';

-- Показать индексы для таблицы
PRAGMA index_list(users);

-- Информация об индексе
PRAGMA index_info(idx_users_email);

-- Удаление индекса
DROP INDEX IF EXISTS idx_users_email;
```

## Транзакции

```sql
-- Начало транзакции
BEGIN TRANSACTION;

-- Или
BEGIN;

-- Эксплицитная транзакция
BEGIN IMMEDIATE;
BEGIN EXCLUSIVE;

-- Откат транзакции
ROLLBACK;

-- Подтверждение транзакции
COMMIT;

-- Пример использования
BEGIN;
INSERT INTO users (username, email) VALUES ('test', 'test@example.com');
INSERT INTO logs (message) VALUES ('User created');
COMMIT;
```

### Автоматические транзакции (в коде):
```python
# Python пример
try:
    conn.execute("BEGIN")
    # операции с БД
    conn.commit()
except:
    conn.rollback()
    raise
```

## Встроенные функции

### Строковые функции:
```sql
SELECT LENGTH('text'); -- Длина строки
SELECT LOWER('TEXT'); -- В нижний регистр
SELECT UPPER('text'); -- В верхний регистр
SELECT SUBSTR('Hello', 2, 3); -- Подстрока: 'ell'
SELECT TRIM('  text  '); -- Убрать пробелы
SELECT REPLACE('Hello World', 'World', 'SQLite'); -- Замена
```

### Числовые функции:
```sql
SELECT ABS(-10); -- Абсолютное значение
SELECT ROUND(3.14159, 2); -- Округление: 3.14
SELECT RANDOM(); -- Случайное число
SELECT MAX(age) FROM users; -- Максимум
SELECT MIN(age) FROM users; -- Минимум
SELECT AVG(age) FROM users; -- Среднее
SELECT SUM(age) FROM users; -- Сумма
SELECT COUNT(*) FROM users; -- Количество
```

### Дата и время:
```sql
SELECT DATE('now'); -- Текущая дата
SELECT TIME('now'); -- Текущее время
SELECT DATETIME('now'); -- Текущая дата и время
SELECT STRFTIME('%Y-%m-%d', 'now'); -- Форматирование даты
SELECT DATE('now', '+1 day'); -- Завтра
SELECT DATE('now', '-1 month'); -- Месяц назад
```

### Условные выражения:
```sql
-- CASE
SELECT username,
    CASE 
        WHEN age < 18 THEN 'Minor'
        WHEN age BETWEEN 18 AND 65 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM users;

-- COALESCE (возвращает первое не NULL значение)
SELECT COALESCE(NULL, 'default', 'backup'); -- 'default'

-- NULLIF (возвращает NULL если значения равны)
SELECT NULLIF('A', 'A'); -- NULL

-- IFNULL (аналогично COALESCE с двумя параметрами)
SELECT IFNULL(NULL, 'default'); -- 'default'
```

## Практические примеры

### Пример 1: Простая БД для блога
```sql
-- Таблица пользователей
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Таблица постов
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Таблица комментариев
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Индексы для ускорения запросов
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_posts_created ON posts(created_at DESC);
```

### Пример 2: Резервное копирование
```bash
# Копирование БД через CLI
sqlite3 source.db ".backup backup.db"

# Копирование с прогрессом
sqlite3 source.db ".backup ? backup.db"

# Экспорт в SQL
sqlite3 source.db ".output dump.sql" ".dump" ".exit"

# Импорт из SQL
sqlite3 new.db < dump.sql
```

### Пример 3: Миграция данных
```sql
-- Создание новой таблицы с улучшенной структурой
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    profile_data JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Копирование данных с преобразованием
INSERT INTO users_new (id, username, email, created_at)
SELECT id, username, email, created_at FROM users;

-- Замена таблицы в транзакции
BEGIN;
DROP TABLE users;
ALTER TABLE users_new RENAME TO users;
COMMIT;
```

## Полезные ссылки

- **Официальный сайт:** https://www.sqlite.org/
- **Документация:** https://www.sqlite.org/docs.html
- **Синтаксис SQL:** https://www.sqlite.org/lang.html
- **Директива PRAGMA:** https://www.sqlite.org/pragma.html
- **Дата и время:** https://www.sqlite.org/lang_datefunc.html
- **Встроенные функции:** https://www.sqlite.org/lang_corefunc.html
- **JSON функции:** https://www.sqlite.org/json1.html
- **Графические инструменты:**
  - DB Browser for SQLite: https://sqlitebrowser.org/
  - SQLite Studio: https://sqlitestudio.pl/
  - Beekeeper Studio: https://www.beekeeperstudio.io/

---
