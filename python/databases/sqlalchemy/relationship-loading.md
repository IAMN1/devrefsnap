# Устранить N+1 и выбрать загрузку отношений

Откройте страницу, если чтение отношений создаёт дополнительные SQL-запросы или возвращает неожиданный состав коллекции.
Выберите приём по нужным данным, а затем проверьте запросы.
[Справочник SQLAlchemy](README.md) · [Схема моделей](models-and-transactions.md#единая-схема-для-рецептов).

## Быстрый поиск

| Ситуация | Приём | Карточка / пример |
| --- | --- | --- |
| SQL появляется внутри цикла по объектам | Посчитать запросы в новой Session | [Найти N+1](#найти-n1) |
| Нужны коллекции для списка родителей | `selectinload` | [Загрузить коллекции](#загрузить-коллекции-через-selectinload) |
| Нужна загрузка через JOIN | `joinedload` | [Коллекция и unique](#загрузить-коллекцию-через-joinedload) · [Одиночная связь](#загрузить-одиночную-связь) |
| Непредвиденная загрузка должна вызвать ошибку | `raiseload` | [Запретить lazy-загрузку](#обнаружить-незапланированную-lazy-загрузку) |
| Фильтр по дочерней таблице; нужна полная коллекция | Явный JOIN + `selectinload` | [Отфильтровать родителей](#отфильтровать-родителей-и-загрузить-полные-коллекции) |
| Нужна только выбранная часть коллекции | JOIN + `contains_eager` | [Загрузить частичную коллекцию](#загрузить-частичную-коллекцию-из-join) |
| Коллекция уже загружена | Учесть Session и `populate_existing` | [Обновить загруженную коллекцию](#обновить-уже-загруженную-коллекцию) |
| Результат не помещается в память | Отдельно выбрать пакетную обработку | [Большие выборки](streaming.md) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; частичные коллекции и состояние Session — продвинутый |
| Предпосылки | SQL JOIN, Session; `demo_models.py` и `seed()` из [подготовки](loading-lab.md#подготовить-примеры) |
| Сверено с документацией | 2026-11-06: SQLAlchemy 2.1, release notes 2.1.8 |
| Выполнено | 2026-11-06: Python 3.14.7, SQLAlchemy 2.1.8, SQLite 3.53.4, pytest 9.2.0; [проверки загрузки](loading-lab.md) |
| Границы | Синхронная ORM и SQLite в памяти; другие драйверы, async и время выполнения здесь не проверялись |

## Выбрать стратегию

| Нужные данные | Приём | Ограничение |
| --- | --- | --- |
| Коллекция каждого родителя | Обычно `selectinload` | Дополнительные SELECT по пакетам ключей; не весь граф одним запросом |
| Коллекция через JOIN | `joinedload` + `Result.unique()` | Строки родителей повторяются в SQL; объём результата может вырасти |
| Одиночная связь, например `Post.author` | Часто `joinedload` | Один JOIN; учитывайте ширину строк и необязательные связи |
| Отношение может не понадобиться | Lazy по умолчанию | Обращение к незагруженному отношению может выполнить SQL |
| Незапланированное чтение отношения | `raiseload` | Ошибка вместо lazy SELECT; это не запрет SQL внутри flush |
| Свой JOIN определяет содержимое коллекции | `contains_eager` | Фильтр может загрузить лишь часть отношения |

Учитывайте число запросов, объём данных и сложность SQL вместе.
Один запрос не гарантирует меньшее время выполнения.
Для many-to-one объект в identity map иногда позволяет обойтись без дополнительного SELECT.
Ниже фрагменты используют подготовленный `engine` и новую Session для каждого сравнения.
[Полные зависимости и подготовка](loading-lab.md#подготовить-примеры) указаны отдельно.

## Найти N+1

**Ситуация:** сначала загружен список пользователей, затем код читает `user.posts` для каждого пользователя.
Без eager loading незагруженные коллекции обычно требуют отдельных SELECT.

**Пример — фрагмент после подготовки учебных данных:**

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from demo_models import User

with Session(engine) as session:
    users = session.scalars(select(User).order_by(User.id)).all()
    sizes = [len(user.posts) for user in users]
```

**Результат учебного набора:** `sizes == [2, 0]`.
В новой Session выполнены три SELECT: один для users и два для posts.
Даже пустая коллекция Bob требует загрузки.
Считайте запросы до конца чтения отношений, включая сериализацию ответа.
Состояние прежней Session может скрыть дополнительные запросы.
[Полный счётчик и сравнение](loading-lab.md#сравнить-стратегии-и-проверить-ограничения) исключают подготовку данных из измерения.

## Загрузить коллекции через selectinload

**Ситуация:** для списка пользователей нужны все посты каждого пользователя.
Добавьте загрузку коллекции в запрос:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(selectinload(User.posts)).order_by(User.id)
    ).all()
    sizes = [len(user.posts) for user in users]
```

**Результат учебного набора:** те же `[2, 0]`, два SELECT вместо трёх.
Для большей выборки число SELECT зависит от числа пакетов ключей и уровней отношений.
Для составного ключа нужен tuple IN; поддержка зависит от СУБД.
Например, SQL Server не поддерживает такой вариант select-in загрузки составного ключа.
Для вложенных comments добавьте `selectinload(User.posts).selectinload(Post.comments)`.
Это отдельный уровень загрузки и дополнительные запросы.
[Проверки количества и содержимого](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Загрузить коллекцию через joinedload

**Ситуация:** коллекцию нужно загрузить через JOIN.
После загрузки коллекции явно удалите повторения ORM-родителей через `unique()`:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(joinedload(User.posts)).order_by(User.id)
    ).unique().all()
    sizes = [len(user.posts) for user in users]
```

**Результат учебного набора:** те же `[2, 0]`, один SELECT.
Без `unique()` SQLAlchemy требует явной обработки повторений и вызывает `InvalidRequestError` при чтении результата.
`unique()` не уменьшает число строк, переданных из БД.
Большие коллекции и несколько JOIN могут заметно увеличить результат SQL.
`joinedload` не заменяет явный `join()` для фильтра по дочерней таблице.
[Проверка успеха и отказа без unique](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Загрузить одиночную связь

**Ситуация:** для списка постов нужен автор каждого поста.
Фрагмент использует связь `Post.author`, которая содержит один объект:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from demo_models import Post

with Session(engine) as session:
    posts = session.scalars(
        select(Post).options(joinedload(Post.author)).order_by(Post.id)
    ).all()
    authors = [post.author.name for post in posts]
```

**Результат учебного набора:** два имени `alice`, один SELECT.
Одиночная связь не размножает строки как коллекция; `unique()` здесь не требуется.
По умолчанию `joinedload` использует LEFT OUTER JOIN и сохраняет родителей без связанного объекта.
Выбор другой стратегии зависит от данных и формы запроса.
[Полная проверка](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Обнаружить незапланированную lazy-загрузку

**Ситуация:** неожиданный SQL при формировании ответа должен стать ошибкой теста.
Разрешите нужное отношение и запретите остальные lazy-загрузки:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, raiseload, selectinload
from demo_models import User

with Session(engine) as session:
    users = session.scalars(
        select(User).options(selectinload(User.posts), raiseload("*")).order_by(User.id)
    ).all()
    sizes = [len(user.posts) for user in users]
    # users[0].profile не загружен: обращение вызовет InvalidRequestError.
```

**Результат:** posts доступны; обращение к незагруженному profile вызывает ошибку вместо SELECT.
Wildcard `"*"` действует и на отношения загруженных дочерних объектов.
`raiseload` относится к отношениям, а не ко всем скалярным колонкам.
Внутренний flush может выполнить нужные загрузки, обходя `raiseload`.
[Проверка ошибки и отсутствия дополнительного SELECT](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Отфильтровать родителей и загрузить полные коллекции

**Ситуация:** нужны пользователи с постом Python, но для каждого пользователя нужны все посты.
Фильтруйте родителей явным JOIN; коллекцию загрузите отдельно:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from demo_models import Post, User

with Session(engine) as session:
    users = session.scalars(
        select(User).join(User.posts).where(Post.title == "Python")
        .options(selectinload(User.posts)).order_by(User.id)
    ).unique().all()
```

**Результат:** выбрана только Alice, её коллекция содержит Python и SQL.
`unique()` убирает возможные повторения родителей после явного JOIN.
Фильтр родителей не превращается автоматически в фильтр содержимого коллекции.
[Сравнение полной и частичной коллекции](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Загрузить частичную коллекцию из JOIN

**Ситуация:** в `User.posts` нужны только посты, выбранные вашим JOIN.
Для новой Session направьте строки JOIN в отношение:

```python
from sqlalchemy import select
from sqlalchemy.orm import Session, contains_eager
from demo_models import Post, User

with Session(engine) as session:
    users = session.scalars(
        select(User).join(User.posts).where(Post.title == "Python")
        .options(contains_eager(User.posts)).order_by(User.id)
    ).unique().all()
```

**Результат:** выбрана Alice, её коллекция содержит только Python.
Это намеренно частичная коллекция; отсутствие SQL в ней не означает удаления поста из БД.
После истечения состояния последующая загрузка может снова вернуть полную коллекцию.
Если коллекция уже загружена, применяйте [следующую карточку](#обновить-уже-загруженную-коллекцию).
[Полная проверка](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Обновить уже загруженную коллекцию

**Ситуация:** Alice уже есть в Session с полной коллекцией posts.
Новый запрос сам по себе не обязан заменить содержимое загруженного отношения.
Фрагмент продолжает работу в этой Session без ожидающих изменений:

```python
from sqlalchemy import select
from sqlalchemy.orm import contains_eager
from demo_models import Post, User

stmt = (
    select(User).join(User.posts).where(Post.title == "Python")
    .options(contains_eager(User.posts))
    .execution_options(populate_existing=True)
)
alice = session.scalars(stmt).unique().one()
```

**Результат:** загруженная коллекция Alice заменяется выбранной частью — только Python.
Перед обновлением решите, как сохранить нужные локальные изменения.
`populate_existing` может заменить значения в памяти; особенно учитывайте отключённый autoflush.
`expire_all()` помечает состояние устаревшим, но не очищает identity map Session.
Последующее чтение может выполнить SQL.
Не передавайте одну Session одновременно нескольким потокам.
[Проверка identity map и повторной загрузки](loading-lab.md#сравнить-стратегии-и-проверить-ограничения)

## Проверить выбор

- [ ] Проверьте состав родителей и коллекций.
- [ ] Посчитайте запросы до окончания чтения нужных отношений.
- [ ] Повторите проверку в новой Session.
- [ ] Проверьте пустые коллекции.
- [ ] Проверьте неожиданный доступ через raiseload.
- [ ] Для больших данных отдельно измерьте объём результата, память и время.

Числа запросов выше получены на двух пользователях и одной коллекции в новом сеансе чтения.
Они не являются оценкой ускорения приложения.
Проверки и условия сравнения находятся в [полном сценарии](loading-lab.md).

## Источники

- [Выбор загрузки отношений](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#what-kind-of-loading-to-use), [select-in](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#select-in-loading), [joined loading](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#joined-eager-loading).
- [Raiseload](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#preventing-unwanted-lazy-loads-using-raiseload), [contains_eager](https://docs.sqlalchemy.org/en/21/orm/queryguide/relationships.html#using-contains-eager-to-load-a-custom-filtered-collection-result), [populate_existing](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#populate-existing).
- [Release notes 2.1.8](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.8).
