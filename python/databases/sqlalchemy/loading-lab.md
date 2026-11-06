# Проверить N+1 и стратегии загрузки

Сравните число SELECT на одинаковых данных и проверьте состав отношений.
Сценарий использует только новую SQLite в памяти.
[Карточки выбора](relationship-loading.md) · [Большие выборки](streaming.md) · [Справочник](README.md).

| Задача | Проверка | Где |
| --- | --- | --- |
| Увидеть N+1 и сравнить eager loading | Содержимое и число SELECT в новых Session | [Полный файл тестов](#сравнить-стратегии-и-проверить-ограничения) |
| Проверить отказ | Joined collection без unique; незагруженное отношение с raiseload | [Тот же файл](#сравнить-стратегии-и-проверить-ограничения) |
| Проверить неполную коллекцию | Фильтр JOIN, identity map и expire | [Тот же файл](#сравнить-стратегии-и-проверить-ограничения) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; состояние Session и contains_eager — продвинутый |
| Предпосылки | Python 3.14, SQLAlchemy и pytest; схема из demo_models.py, данные из demo_queries.py |
| Сверено с документацией | 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8 |
| Выполнено | 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0, greenlet 3.5.6; 15 проверок полного файла ниже |
| Не измерялось | Время, память, сетевые задержки и планы запросов рабочей БД |

## Подготовить примеры

Создайте отдельную учебную папку и виртуальное окружение.
Сохраните [полную схему](models-and-transactions.md#единая-схема-для-рецептов) как `demo_models.py`.
Сохраните [подготовку данных и запросы](queries.md#select-join-подзапросы-и-cte) как `demo_queries.py`.
Сохраните блок ниже как `test_relationship_loading.py` рядом с этими файлами.
Установите проверенные версии в учебное окружение:

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.8' 'pytest==9.2.0'
```

Extra `asyncio` устанавливает greenlet, необходимый импорту AsyncAttrs из общей модели.
Это требование модели, хотя проверки загрузки ниже синхронные.
В проверенном окружении использовался greenlet 3.5.6.

Исходный `seed()` создаёт Alice с постами Python и SQL, а также Bob без постов.
Фикстура создаёт отдельную БД для каждого теста.
Некоторые сравнения добавляют ещё трёх пользователей без постов.
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


@pytest.mark.parametrize("eager, expected_count", [(False, 2), (True, 1)])
def test_scalar_author_and_identity_map(engine, eager, expected_count):
    with count_selects(engine) as statements, Session(engine) as session:
        stmt = select(Post).order_by(Post.id)
        if eager:
            stmt = stmt.options(joinedload(Post.author))
        posts = session.scalars(stmt).all()
        assert [post.author.name for post in posts] == ["alice", "alice"]
        assert posts[0].author is posts[1].author
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
**Результат:** все проверки проходят.
Тест после закрытия Session не выполняет commit и не вызывает expire.
Если состояние истекло до закрытия, этот тест не гарантирует доступ к данным без Session.

## Прочитать результаты сравнения

Числа ниже проверяются в `test_same_collections_and_select_counts`.
Условия: одна коллекция `User.posts`, новые Session, одинаковый состав данных и полное чтение коллекций.

| Пользователи | Lazy | Select-in | Joined |
| --- | --- | --- | --- |
| Alice и Bob | 3 SELECT | 2 SELECT | 1 SELECT |
| Те же и три пользователя без постов | 6 SELECT | 2 SELECT | 1 SELECT |

Для двух постов одного автора lazy many-to-one даёт два SELECT суммарно, а не три.
Identity map переиспользует уже загруженного автора.
Вложенная загрузка comments даёт третий SELECT в отдельном тесте.
Результаты относятся только к этим условиям и версиям.
Они не измеряют ускорение, память и сетевой трафик приложения.

## Источники

- [Greenlet и установка в SQLAlchemy 2.1](https://docs.sqlalchemy.org/en/21/faq/installation.html#i-m-getting-an-error-about-greenlet-not-being-installed-when-i-try-to-use-asyncio).

- [Загрузка отношений](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html), [события выполнения SQL](https://docs.sqlalchemy.org/en/21/core/events.html#sqlalchemy.events.ConnectionEvents.before_cursor_execute).
- [Populate existing](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#populate-existing), [release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
