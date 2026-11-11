# Проверить N+1 и стратегии загрузки

Сравните число SELECT на одинаковых данных и проверьте состав отношений.
Сценарий использует только новую SQLite в памяти.
[Карточки выбора](relationship-loading.md) · [Большие выборки](streaming.md) · [Справочник](README.md).
Для первого знакомства с N+1 начните с [двух моделей в одном файле](../../../docs/ru/python/databases/sqlalchemy/n-plus-one.md#подготовка-и-запуск).
Для частичных коллекций, вложенных связей и состояния Session используйте расширенную схему ниже.

| Задача | Проверка | Где |
| --- | --- | --- |
| Увидеть N+1 и сравнить eager loading | Содержимое и число SELECT в новых Session | [Полный файл тестов](#сравнить-стратегии-и-проверить-ограничения) |
| Проверить отказ | Joined collection без unique; незагруженное отношение с raiseload | [Тот же файл](#сравнить-стратегии-и-проверить-ограничения) |
| Проверить страницу родителей и необязательную связь | LIMIT сохраняет полные коллекции; LEFT OUTER JOIN сохраняет родителей без связи | [Тот же файл](#сравнить-стратегии-и-проверить-ограничения) |
| Проверить неполную коллекцию | Фильтр JOIN, identity map и expire | [Тот же файл](#сравнить-стратегии-и-проверить-ограничения) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; состояние Session и contains_eager — продвинутый |
| Предпосылки | Python 3.14, SQLAlchemy и pytest; схема из demo_models.py, данные из demo_queries.py |

## Подготовить примеры

Создайте отдельную учебную папку и виртуальное окружение.
Сохраните [полную схему](models-and-transactions.md#единая-схема-для-рецептов) как `demo_models.py`.
Сохраните [подготовку данных и запросы](queries.md#select-join-подзапросы-и-cte) как `demo_queries.py`.
Сохраните блок ниже как `test_relationship_loading.py` рядом с этими файлами.
Установите зависимости в учебное окружение:

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'pytest==9.2.0'
```

Extra `asyncio` устанавливает greenlet, необходимый импорту AsyncAttrs из общей модели.
Это требование модели, хотя проверки загрузки ниже синхронные.
Используйте Python 3.14 и SQLite из стандартного модуля `sqlite3`.

Исходный `seed()` создаёт Alice с постами Python и SQL, а также Bob без постов.
Фикстура создаёт отдельную БД для каждого теста.
Некоторые сравнения добавляют ещё трёх пользователей без постов.
Два поста ссылаются на одного автора Alice.
Связь `User.manager` необязательна: руководитель Bob — Alice, а у Alice руководителя нет.
Все сравниваемые загрузки начинают чтение в новой Session.
Запись данных и создание таблиц не входят в счётчик SELECT.

Для коротких карточек подготовьте `engine` этим фрагментом после сохранения двух модулей:

```python
from sqlalchemy.orm import Session
from demo_models import new_engine
from demo_queries import seed

engine = new_engine()
with Session(engine) as session, session.begin():
    seed(session)
```

После проверки карточек выполните `engine.dispose()`.
Фикстура полного теста освобождает engine автоматически.

## Сравнить стратегии и проверить ограничения

Полный файл `test_relationship_loading.py` считает SELECT, выполненные этим engine.
Счётчик перехватывает SQL от драйвера; он не оценивает стоимость плана.
Чтение `user.posts` входит в измерение.
Отношения сначала не загружены, кроме явно названных проверок identity map.

<!-- example: sqlalchemy/test_relationship_loading.py -->
```python
from contextlib import contextmanager

import pytest
from sqlalchemy import event, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session, contains_eager, joinedload, raiseload, selectinload

from demo_models import Post, User, new_engine
from demo_queries import seed


@contextmanager
def count_selects(engine):
    statements = []

    def before_cursor_execute(connection, cursor, statement, parameters, context, many):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        yield statements
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)


@pytest.fixture
def engine():
    engine = new_engine()
    try:
        with Session(engine) as session, session.begin():
            seed(session)
        yield engine
    finally:
        engine.dispose()


@pytest.mark.parametrize("extra_users", [0, 3])
@pytest.mark.parametrize("strategy", ["lazy", "selectin", "joined"])
def test_same_collections_and_select_counts(engine, extra_users, strategy):
    with Session(engine) as session, session.begin():
        session.add_all([
            User(name=f"extra-{i}", email=f"extra-{i}@example.com")
            for i in range(extra_users)
        ])
    expected = {"alice": ["Python", "SQL"], "bob": []}
    expected.update({f"extra-{i}": [] for i in range(extra_users)})
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(User).order_by(User.id)
        if strategy == "selectin":
            stmt = stmt.options(selectinload(User.posts))
        elif strategy == "joined":
            stmt = stmt.options(joinedload(User.posts))
        result = session.scalars(stmt)
        if strategy == "joined":
            result = result.unique()
        users = result.all()
        actual = {user.name: sorted(post.title for post in user.posts) for user in users}
        assert actual == expected
    expected_count = {"lazy": 3 + extra_users, "selectin": 2, "joined": 1}[strategy]
    assert len(statements) == expected_count


def test_joined_collection_requires_unique(engine):
    with Session(engine) as session:
        result = session.scalars(select(User).options(joinedload(User.posts)))
        with pytest.raises(InvalidRequestError, match="unique"):
            result.all()


@pytest.mark.parametrize("strategy, expected_count", [("lazy", 2), ("selectin", 2), ("joined", 1)])
def test_scalar_author_and_identity_map(engine, strategy, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(Post).order_by(Post.id)
        if strategy == "selectin":
            stmt = stmt.options(selectinload(Post.author))
        elif strategy == "joined":
            stmt = stmt.options(joinedload(Post.author))
        posts = session.scalars(stmt).all()
        assert [post.author.name for post in posts] == ["alice", "alice"]
        assert posts[0].author is posts[1].author
    assert len(statements) == expected_count


def test_joined_collection_sql_rows_repeat_parent(engine):
    stmt = select(User).options(joinedload(User.posts)).order_by(User.id)
    # Connection возвращает строки SQL без сборки ORM-объектов и без unique().
    with engine.connect() as connection:
        rows = connection.execute(stmt).mappings().all()
    assert [row["name"] for row in rows] == ["alice", "alice", "bob"]
    assert len(rows) == 3


@pytest.mark.parametrize("loader, expected_count", [(selectinload, 2), (joinedload, 1)])
def test_parent_limit_keeps_full_collection(engine, loader, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(User).options(loader(User.posts)).order_by(User.id).limit(1)
        result = session.scalars(stmt)
        if loader is joinedload:
            result = result.unique()
        users = result.all()
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == ["Python", "SQL"]
    assert len(statements) == expected_count


def test_explicit_join_limit_counts_rows_before_unique(engine):
    with Session(engine) as session, session.begin():
        bob = session.scalar(select(User).where(User.name == "bob"))
        session.add(Post(title="Bob post", author=bob))
    stmt = (
        select(User).join(User.posts).options(selectinload(User.posts))
        .order_by(User.id, Post.id)
    )
    with Session(engine) as session:
        all_users = session.scalars(stmt).unique().all()
        assert {user.name: sorted(post.title for post in user.posts) for user in all_users} == {
            "alice": ["Python", "SQL"], "bob": ["Bob post"],
        }
    with Session(engine) as session:
        users = session.scalars(stmt.limit(2)).unique().all()
        # Лимит двух строк JOIN оставляет одного родителя с двумя постами.
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == ["Python", "SQL"]


@pytest.mark.parametrize("loader, expected_count", [(selectinload, 2), (joinedload, 1)])
def test_optional_scalar_keeps_parents(engine, loader, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(loader(User.manager)).order_by(User.id)
        ).all()
        assert [(user.name, user.manager.name if user.manager else None) for user in users] == [
            ("alice", None), ("bob", "alice"),
        ]
        assert users[1].manager is users[0]
    assert len(statements) == expected_count


def test_raiseload_allows_posts_and_rejects_other_relationships(engine):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(selectinload(User.posts), raiseload("*")).order_by(User.id)
        ).all()
        assert [len(user.posts) for user in users] == [2, 0]
        assert len(statements) == 2
        with pytest.raises(InvalidRequestError):
            _ = users[0].profile
        with pytest.raises(InvalidRequestError):
            _ = users[0].posts[0].comments
        assert len(statements) == 2


def test_nested_selectin_loads_comments_without_later_selects(engine):
    with count_selects(engine) as statements, Session(engine) as session:
        users = session.scalars(
            select(User).options(
                selectinload(User.posts).selectinload(Post.comments), raiseload("*")
            ).order_by(User.id)
        ).all()
        comments = sorted(
            comment.text for user in users for post in user.posts for comment in post.comments
        )
        assert comments == ["Useful"]
        assert len(statements) == 3


@pytest.mark.parametrize("partial, expected_titles, expected_count", [
    (False, ["Python", "SQL"], 2),
    (True, ["Python"], 1),
])
def test_filter_parents_and_choose_collection_content(engine, partial, expected_titles, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        option = contains_eager(User.posts) if partial else selectinload(User.posts)
        users = session.scalars(
            select(User).join(User.posts).where(Post.title == "Python")
            .options(option).order_by(User.id)
        ).unique().all()
        assert [user.name for user in users] == ["alice"]
        assert sorted(post.title for post in users[0].posts) == expected_titles
    assert len(statements) == expected_count


def test_existing_collection_requires_explicit_refresh(engine):
    with Session(engine) as session:
        alice = session.scalar(
            select(User).where(User.name == "alice").options(selectinload(User.posts))
        )
        assert sorted(post.title for post in alice.posts) == ["Python", "SQL"]
        stmt = (
            select(User).join(User.posts).where(Post.title == "Python")
            .options(contains_eager(User.posts))
        )
        same = session.scalars(stmt).unique().one()
        assert same is alice
        assert sorted(post.title for post in same.posts) == ["Python", "SQL"]
        refreshed = session.scalars(stmt.execution_options(populate_existing=True)).unique().one()
        assert refreshed is alice
        assert [post.title for post in refreshed.posts] == ["Python"]
        alice_id = alice.id
        session.expire_all()
        assert session.get(User, alice_id) is alice
        assert sorted(post.title for post in alice.posts) == ["Python", "SQL"]


def test_eager_collection_is_available_after_session_close(engine):
    with Session(engine) as session:
        users = session.scalars(
            select(User).options(selectinload(User.posts)).order_by(User.id)
        ).all()
    assert [len(user.posts) for user in users] == [2, 0]
```

Запустите `python -m pytest -q test_relationship_loading.py`.
**Ожидаемый результат:** все проверки проходят.
Тест после закрытия Session не выполняет commit и не вызывает expire.
Если состояние истекло до закрытия, этот тест не гарантирует доступ к данным без Session.

## Прочитать результаты сравнения

Числа ниже проверяются в `test_same_collections_and_select_counts`.
Условия: одна коллекция `User.posts`, новые Session, одинаковый состав данных и полное чтение коллекций.

| Пользователи | Lazy | Select-in | Joined |
| --- | --- | --- | --- |
| Alice и Bob | 3 SELECT | 2 SELECT | 1 SELECT |
| Те же и три пользователя без постов | 6 SELECT | 2 SELECT | 1 SELECT |

Для одиночной связи `Post.author` тест сравнивает те же два поста одного автора в новых Session.
Many-to-one означает, что многие посты могут ссылаться на одного автора.

| Способ загрузки автора | SELECT вместе с чтением постов | Состав объектов |
| --- | --- | --- |
| Lazy | 2 | Два поста и один общий объект Alice |
| Select-in | 2 | Те же объекты; автор прочитан отдельным SELECT |
| Joined | 1 | Те же объекты; поля автора присутствуют в обеих строках SQL |

Identity map — хранилище уже загруженных объектов по идентификатору внутри Session.
Identity map переиспользует автора и при lazy-загрузке исключает второй SELECT для Alice.
Это не устраняет повторение полей автора в SQL при joinedload.
Тест `test_joined_collection_sql_rows_repeat_parent` отдельно показывает три строки SQL для двух пользователей.
Две строки содержат Alice с её постами; третья сохраняет Bob без постов.
Число строк SQL отличается от числа ORM-объектов, возвращённых после `unique()`.

Тест страницы с `LIMIT 1` проверяет одного пользователя и оба его поста при обеих стратегиях.
Отдельный тест явного JOIN показывает, почему `LIMIT 2` не гарантирует двух разных родителей.
Тест `User.manager` проверяет сохранение Alice со значением `None` при обеих стратегиях.
Без `unique()` чтение joinedload коллекции завершается `InvalidRequestError` в отдельном тесте.
Вложенная загрузка comments даёт третий SELECT в отдельном тесте.
Результаты относятся только к этим условиям и версиям.
Они не измеряют ускорение, память и сетевой трафик приложения.
Другие СУБД, составные ключи, блокировки и конкурентный доступ требуют отдельных проверок.

## Источники

- [Greenlet и установка в SQLAlchemy 2.1](https://docs.sqlalchemy.org/en/21/faq/installation.html#i-m-getting-an-error-about-greenlet-not-being-installed-when-i-try-to-use-asyncio).

- [Загрузка отношений](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html), [события выполнения SQL](https://docs.sqlalchemy.org/en/21/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute).
- [Populate existing](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#populate-existing), [release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
