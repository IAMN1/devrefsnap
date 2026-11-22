
# Проверить N+1 и стратегии загрузки

[English](../../../../en/python/databases/sqlalchemy/loading-lab.md)

Сравните число SELECT на одинаковых данных и проверьте состав отношений.
Сценарий использует только новую SQLite в памяти.
[Карточки выбора](relationship-loading.md) · [Большие выборки](streaming.md) · [Справочник](README.md).
Для первого знакомства с N+1 начните с [двух моделей в одном файле](n-plus-one.md#подготовка-и-запуск).
Расширенная схема ниже нужна для вложенных связей и [карточек фильтрации и обновления коллекций](filtered-relationships.md).

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
Сохраните файл [`test_relationship_loading.py`](../../../../../examples/python/databases/sqlalchemy/test_relationship_loading.py) рядом с этими файлами.
Установите зависимости в учебное окружение:

```bash
python -m pip install 'sqlalchemy[asyncio]==2.1.9' 'pytest==9.2.0'
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

[`sqlalchemy/test_relationship_loading.py`](../../../../../examples/python/databases/sqlalchemy/test_relationship_loading.py)

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
- [Populate existing](https://docs.sqlalchemy.org/en/21/orm/queryguide/api.html#populate-existing), [release notes 2.1.9](https://docs.sqlalchemy.org/en/21/changelog/changelog_21.html#change-2.1.9).
