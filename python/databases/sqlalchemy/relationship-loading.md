# Устранить N+1 и выбрать загрузку отношений

Откройте страницу, если чтение отношений создаёт дополнительные SQL-запросы или возвращает неожиданный состав коллекции.
Выберите приём по нужным данным, а затем проверьте запросы.
[Справочник SQLAlchemy](README.md) · [Схема моделей](models-and-transactions.md#единая-схема-для-рецептов).
Для первого знакомства откройте [самостоятельный синхронный пример N+1](n-plus-one.md#подготовка-и-запуск): две модели в одном файле.

## Быстрый поиск

| Ситуация | Приём | Карточка / пример |
| --- | --- | --- |
| Слишком много запросов к БД при чтении коллекций | Посчитать запросы в новой Session | [Найти N+1](#найти-n1) · [Самостоятельная программа](n-plus-one.md#полная-программа) |
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
| Предпосылки | Для N+1 — Python и основы SELECT: [один файл с объяснениями](n-plus-one.md). Остальные карточки используют SQL JOIN, Session, `demo_models.py` и `seed()` из [подготовки лабораторной](loading-lab.md#подготовить-примеры) |
| Самостоятельный N+1 | [Отдельная программа, версии и границы](n-plus-one.md#результат-и-ограничения); [расширенный набор](loading-lab.md) использует общую схему |
| Среда примеров | Синхронная ORM SQLAlchemy 2.1.8 и SQLite 3.53.4 в памяти; [подготовка](loading-lab.md#подготовить-примеры) |

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
Карточка N+1 использует [самостоятельную программу](n-plus-one.md).
Остальные фрагменты используют подготовленный `engine` и новую Session для каждого сравнения.
[Полные зависимости и подготовка](loading-lab.md#подготовить-примеры) указаны отдельно.

## Найти N+1

**Ситуация:** сначала загружен список пользователей, затем код читает `user.posts` для каждого пользователя.
`User.posts` — отношение ORM: коллекция объектов `Post`, связанных с пользователем.
ORM связывает строки таблиц с объектами Python.
При lazy-загрузке первое чтение незагруженной коллекции выполняет SELECT.
Для N пользователей получается N+1 запросов: один для списка и N для коллекций.

**Предпосылки:** классы, функции, циклы Python и основы SQL SELECT.
[Подготовка и запуск](n-plus-one.md#подготовка-и-запуск) требуют Python 3.14.7 и SQLAlchemy 2.1.8.
[Полная программа](n-plus-one.md#полная-программа) содержит две модели, создаёт SQLite в памяти и записывает учебные данные.

**Пример — фрагмент функции `read_users` из этой программы без предварительной загрузки:**

```python
stmt = select(User).order_by(User.id)
users = session.scalars(stmt).all()
rows = [(user.name, sorted(post.title for post in user.posts)) for user in users]
```

`session` — новая `Session` внутри `read_users`; сессия выполняет запросы и хранит состояние объектов.
`select(User)` описывает запрос, а `session.scalars(stmt).all()` выполняет запрос и возвращает список пользователей.

**Изменение:** добавьте `.options(selectinload(User.posts))` к запросу пользователей.
Этот приём заранее читает посты для группы пользователей отдельным SELECT с условием `IN`.
Такую предварительную загрузку называют eager loading.
[Полная программа сравнивает оба варианта](n-plus-one.md#полная-программа) и считает SELECT до конца чтения коллекций.

**Результат учебного набора:** `[('alice', ['Python', 'SQL']), ('bob', [])]` в обоих вариантах.
Новая Session с lazy-загрузкой выполняет три SELECT, а с `selectinload` — два.
Даже пустая коллекция Bob требует загрузки.
Считайте запросы до конца чтения отношений, включая сериализацию ответа.
Состояние прежней Session может скрыть дополнительные запросы.
Число запросов зависит от объёма и формы загрузки; два SELECT не являются общей гарантией.
[Ограничения минимального примера](n-plus-one.md#результат-и-ограничения) и [полная лабораторная](loading-lab.md#сравнить-стратегии-и-проверить-ограничения) описаны отдельно.

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

**Результат учебного набора:** `sizes == [2, 0]`, два SELECT вместо трёх.
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
