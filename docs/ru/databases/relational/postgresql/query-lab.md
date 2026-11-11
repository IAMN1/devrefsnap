
# Подготовить учебную базу PostgreSQL

[English](../../../../en/databases/relational/postgresql/query-lab.md)

Пример создаёт пользователей, товары и заказы для карточек PostgreSQL.
Пример создаёт новую БД `cheatsheet_demo` на отдельном сервере.
[К карточкам запросов](queries.md) · [К PostgreSQL](README.md).

Нужны PostgreSQL 18, `createdb`, `psql` и роль с правом создать учебную БД.


## Полный пример: учебная база

Подготовьте отдельный учебный сервер или кластер.
Команды оболочки ниже рассчитаны на локальный сервер с ролью `postgres`.
При другой установке замените адрес и роль.
Пароль вводится по запросу или берётся из настроенного password file.

Сохраните файл [`queries.sql`](../../../../../examples/databases/relational/postgresql/queries.sql) в текущем каталоге.
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

[`queries.sql`](../../../../../examples/databases/relational/postgresql/queries.sql)

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
