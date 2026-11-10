# Устранить лишние запросы при чтении коллекции

Откройте страницу, если цикл по пользователям выполняет отдельный SQL-запрос для постов каждого пользователя.
Пример сравнивает два способа чтения одинаковых данных.
Программа содержит две синхронные модели и запускается из одного файла.

| Нужно сделать | Приём | Где |
| --- | --- | --- |
| Понять причину лишних запросов | Различить lazy-загрузку и eager loading | [Термины и изменение запроса](#почему-возникает-n1) |
| Повторить пример с нуля | Установить SQLAlchemy и создать один файл | [Подготовка и запуск](#подготовка-и-запуск) · [Полная программа](#полная-программа) |
| Проверить другие стратегии и сложные случаи | Сравнить joinedload, raiseload и частичные коллекции | [Отдельная лабораторная](loading-lab.md) |

Уровень: средний; первое знакомство с загрузкой отношений ORM.
Предпосылки: функции и классы Python, аннотации типов, циклы, `with`, `try`/`finally`, `assert` и основы SQL SELECT.

Для запуска нужны Python 3.14, SQLAlchemy 2.1.8 и встроенный модуль `sqlite3`.

Пример использует SQLite в памяти и синтетические данные.
После завершения программы учебные данные исчезают.

## Почему возникает N+1

**Ситуация:** нужно показать список пользователей вместе с постами каждого пользователя.
Первый SELECT читает пользователей.
Затем чтение незагруженного `user.posts` выполняет ещё один SELECT для каждого пользователя.
Для N пользователей получается N+1 запросов: один общий и N дополнительных.
Пустая коллекция тоже требует проверки в БД.

ORM связывает строки таблиц с объектами Python.
Здесь модель `User` описывает пользователя, а модель `Post` — его пост.
Отношение `User.posts` представляет коллекцию постов одного пользователя.
`relationship` описывает это отношение в Python; `ForeignKey` указывает столбец связи между таблицами.

**Изменение:** загрузите посты заранее через `selectinload(User.posts)`.
Lazy loading означает загрузку отношения при первом обращении к незагруженному атрибуту.
Eager loading означает загрузку отношения при выполнении исходного запроса, до последующего обращения к атрибуту.
`selectinload` — способ eager loading: отдельный SELECT читает посты сразу для группы пользователей через условие `IN`.

**Фрагмент функции `read_users` из [полной программы](#полная-программа):**

```python
stmt = select(User).options(selectinload(User.posts)).order_by(User.id)
```

`select(User)` описывает запрос; само описание ещё не выполняет SQL.
`Session` выполняет запрос и хранит состояние загруженных объектов.
В примере `session.scalars(stmt).all()` возвращает список объектов `User`.
Каждое сравнение использует новую `Session`, поэтому ранее загруженные посты не скрывают дополнительные SELECT.

**Результат:** для двух пользователей число SELECT уменьшается с трёх до двух при том же составе постов.
Для больших выборок `selectinload` выполняет запросы по пакетам ключей; два SELECT не являются общей гарантией.
Для составного ключа нужна поддержка tuple IN со стороны СУБД.
Для выбора другой стратегии откройте [таблицу решений](relationship-loading.md#выбрать-стратегию).

## Подготовка и запуск

Создайте отдельную папку `sqlalchemy-n-plus-one-demo`.
Сохраните [полную программу ниже](#полная-программа) как `n_plus_one.py` в этой папке.
Откройте терминал в папке `sqlalchemy-n-plus-one-demo`.
Используйте Python 3.14 для создания окружения.
Выполните команды оболочки на macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'sqlalchemy==2.1.8'
python n_plus_one.py
```

Программе достаточно SQLAlchemy и стандартной библиотеки Python.
`pytest`, `AsyncAttrs`, extra `asyncio` и `greenlet` этому примеру не нужны.
Установка требует доступа к индексу пакетов; сама программа работает без внешней сети.

## Полная программа

Полный файл `n_plus_one.py` определяет модели, создаёт таблицы, записывает данные и проверяет результаты.
`DeclarativeBase` задаёт общую основу моделей.
`Mapped` указывает тип ORM-атрибута, а `mapped_column` настраивает столбец таблицы.
`back_populates` связывает атрибуты `User.posts` и `Post.author` в обе стороны.
`Engine` управляет соединениями с БД; объект `engine` создаётся в `main`.
`with session.begin()` фиксирует учебные данные при успехе и откатывает транзакцию при исключении.

Функция счётчика получает SQL через событие `before_cursor_execute` перед выполнением команды драйвером.
Счётчик подключается только на время чтения и включает обращения к `user.posts`.
Создание таблиц и запись данных находятся вне измерения.
Блок `finally` снимает обработчик события даже при исключении.

<!-- example: sqlalchemy/n_plus_one.py -->
```python
from sqlalchemy import ForeignKey, create_engine, event, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, selectinload


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped[User] = relationship(back_populates="posts")


def read_users(engine, *, eager=False):
    statements = []

    def count_select(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", count_select)
    try:
        with Session(engine) as session:
            stmt = select(User).order_by(User.id)
            if eager:
                stmt = stmt.options(selectinload(User.posts))
            users = session.scalars(stmt).all()
            rows = [(user.name, sorted(post.title for post in user.posts)) for user in users]
        return rows, len(statements)
    finally:
        event.remove(engine, "before_cursor_execute", count_select)


def main():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session, session.begin():
            session.add_all([
                User(name="alice", posts=[Post(title="Python"), Post(title="SQL")]),
                User(name="bob", posts=[]),
            ])

        expected = [("alice", ["Python", "SQL"]), ("bob", [])]
        lazy_rows, lazy_count = read_users(engine)
        eager_rows, eager_count = read_users(engine, eager=True)
        assert lazy_rows == eager_rows == expected
        assert lazy_count == 3
        assert eager_count == 2
        print(f"lazy: {lazy_count} SELECT; {lazy_rows}")
        print(f"selectinload: {eager_count} SELECT; {eager_rows}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
```

## Результат и ограничения

Ожидаемый вывод:

```text
lazy: 3 SELECT; [('alice', ['Python', 'SQL']), ('bob', [])]
selectinload: 2 SELECT; [('alice', ['Python', 'SQL']), ('bob', [])]
```

В обоих случаях прочитаны все пользователи и все посты, включая пустую коллекцию Bob.
Проверки `assert` сравнивают состав данных и число запросов отдельно.
Запускайте пример без `python -O`, чтобы сохранить проверки `assert`.

Счётчик распознаёт команды, начинающиеся с SELECT; этого достаточно для запросов данного примера.
Для произвольного SQL с CTE или комментариями нужен другой способ учёта команд.
Числа относятся к одной коллекции, двум пользователям и новым `Session` на указанных версиях.
Они не измеряют время выполнения и не доказывают ускорение приложения.

Для своих данных отдельно измерьте объём результата, время и память.

Сравнение `joinedload`, отказ без `unique()`, `raiseload`, вложенные и частичные коллекции находятся в [полной лабораторной](loading-lab.md).
Лабораторная использует расширенную схему с отдельной подготовкой.
Async, другие СУБД, большие объёмы и конкурентный доступ этот пример не проверяет.

## Источники

- [SQLAlchemy 2.1: lazy loading и проблема N+1](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#lazy-loading).
- [Select-in loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#select-in-loading).
- [Основы ORM](https://docs.sqlalchemy.org/en/21/orm/quickstart.html), [Session](https://docs.sqlalchemy.org/en/21/orm/session_basics.html).
- [События выполнения SQL](https://docs.sqlalchemy.org/en/21/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute).
- [Release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).

[Карточки загрузки](relationship-loading.md) · [Справочник SQLAlchemy](README.md) · [Указатель задач](../../../tasks/README.md#sql-и-доступ-из-python)
