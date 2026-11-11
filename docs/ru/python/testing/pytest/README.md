
# pytest

[English](../../../../en/python/testing/pytest/README.md)

Используйте pytest для проверки поведения Python-программы через assertions, фикстуры, параметризацию и плагины.
Несколько связанных утверждений могут проверять один сценарий.
Правило «один assert на тест» не является требованием pytest.


## Быстрый поиск

Выполняйте отдельные команды в каталоге тестового проекта.
Используйте `python` из нужного окружения.

| Задача | Команда / API | Подробнее |
| --- | --- | --- |
| Запустить тесты | `python -m pytest` | [Конфигурация](configuration.md) |
| Конкретный тест | `python -m pytest test_basics.py::test_database_write` | [Полный пример](fixtures.md) |
| Подробный вывод | `python -m pytest -v` | [Отладка](configuration.md#выбор-тестов-и-отладка) |
| Подстрока имени / marker | `-k 'subtotal'` / `-m 'not slow'` | [Выбор тестов](configuration.md#выбор-тестов-и-отладка) |
| Ожидаемая ошибка | `pytest.raises(ValueError, match='quantity')` | [Assertions](fixtures.md) |
| Приближённое число | `pytest.approx(0.3)` | [Assertions](fixtures.md) |
| Временный путь / вывод | `tmp_path`, `capsys` | [Фикстуры](fixtures.md) |
| Подменить зависимость | `monkeypatch`, `mocker.patch` | [Моки](mocking-and-async.md) |
| Async-тест | `@pytest.mark.asyncio` + pytest-asyncio | [Async](mocking-and-async.md) |
| JUnit-отчёт | `--junitxml=report.xml` | [CI](configuration.md#плагины-и-отчёты) |

| Параметр | Значение |
| --- | --- |
| Ветка API | pytest 9; отдельные возможности предоставляют плагины |
| Предпосылки | Python, изолированное окружение; базовое понимание функций и исключений |

<a id="навигация"></a>

<a id="базовый-уровень"></a>

Для воспроизведения используйте [точные зависимости примеров](configuration.md#среда-примеров).


## Написать осмысленный тест

**Ситуация:** `subtotal(3, 2.5)` должен вернуть `7.5`, а отрицательное количество должно дать ошибку.
**Изменение:** задайте ожидаемый результат независимо от реализации.
Фрагмент тестового файла использует [полный `demo_service.py`](fixtures.md#полный-учебный-пример):

```python
import pytest
from demo_service import subtotal


def test_subtotal_and_rejection():
    assert subtotal(3, 2.5) == pytest.approx(7.5)
    with pytest.raises(ValueError, match="quantity"):
        subtotal(-1, 2.5)
```

**Результат:** тест проходит для заданного поведения и падает при пропущенной проверке отрицательного количества.
Допуск для приближённых чисел выбирайте по смыслу данных.
[Полный набор и команда запуска](fixtures.md#полный-учебный-пример).


Создайте отдельное окружение: `python -m venv .venv`.
Установите pytest в это окружение: `python -m pip install pytest`.
В uv-проекте удобнее `uv add --dev pytest` и `uv run pytest`.
Подробности находятся в [справочнике uv](../../tooling/uv/README.md).
Тест содержит подготовку данных, действие и проверку наблюдаемого результата.
Он должен падать при неправильном поведении программы.

По умолчанию pytest ищет файлы `test_*.py` / `*_test.py`, функции `test_*` и методы в классах `Test*` без собственного `__init__`.
`conftest.py` распространяет фикстуры на свой каталог и вложенные каталоги.
Импортировать `conftest.py` вручную не нужно.
Большой проект может размещать код в `src/package/`, а тесты в `tests/`.
Установите пакет в тестовое окружение.

[Полный пример](fixtures.md) включает саму функцию, импорты, фикстуру БД и проверку ошибки входных данных.

<a id="средний-уровень"></a>


## Управлять подготовкой и вариантами данных

**Ситуация:** два теста должны получить независимые списки.
**Изменение:** создавайте список в function-scoped фикстуре.
Самостоятельный тестовый модуль требует pytest:

```python
import pytest


@pytest.fixture
def names():
    return []


def test_append(names):
    names.append("alice")
    assert names == ["alice"]


def test_empty(names):
    assert names == []
```

**Результат:** оба теста проходят независимо от порядка.
Если увеличить scope, изменяемый список начнут разделять несколько тестов.
[Полные примеры с ресурсами и параметрами](fixtures.md).


pytest передаёт fixture по имени в аргумент теста.
`yield` отделяет setup от teardown.
Если setup падает до yield, код после yield этой fixture не выполняется.
При нескольких ресурсах задавайте освобождение каждого ресурса сразу после его успешного создания.
Для этого используйте отдельную fixture или контекст.

Схема показывает вызовы подготовки, теста и освобождения ресурса:

```mermaid
flowchart LR
    A[Запрос fixture] -->|создать ресурс| B[Подготовка ресурса]
    B -->|передать значение| C[yield: передать тесту]
    C -->|вызвать тест| D[Тест: успех или исключение]
    D -->|завершить использование| E[Teardown ресурса]
```

`@pytest.mark.parametrize` запускает независимые сценарии с конкретными ожидаемыми значениями.
`tmp_path`, `capsys`, `monkeypatch` помогают изолировать файлы, вывод и окружение.
[Примеры и границы scope](fixtures.md#область-действия-и-фабрики) позволяют избежать зависимости от порядка тестов.

<a id="продвинутый-уровень"></a>


## Проверять границы без реальных внешних сервисов

**Ситуация:** `status_label(7)` должен оформить ответ адаптера без обращения к реальному сервису.
**Изменение:** подмените имя в модуле, который использует адаптер.
Фрагмент требует pytest-mock и [полный `demo_service.py`](fixtures.md#полный-учебный-пример):

```python
import demo_service


def test_status_label(mocker):
    adapter = mocker.patch("demo_service.read_remote", return_value={"status": "ready"})
    assert demo_service.status_label(7) == "order 7: ready"
    adapter.assert_called_once_with(7)
```

**Результат:** тест проверяет текст и передачу id внешнему адаптеру.
Тест не проверяет реализацию реального сервиса.
[Полный модуль с отказом и async](mocking-and-async.md#проверить-внешний-контракт-без-сети).


Подменяйте сеть или внешний адаптер в месте, где тестируемый модуль ищет объект.
Проверяйте результат для пользователя.
Проверяйте существенный контракт вызова.
Не закрепляйте произвольное число внутренних вызовов.
[Моки и async](mocking-and-async.md) содержат реальные тесты без HTTP-запросов.

[Конфигурация и плагины](configuration.md) разделяют возможности pytest, pytest-asyncio, pytest-mock, pytest-cov и xdist.
Параллельный запуск требует независимых данных.
При параллельном запуске session fixture создаётся отдельно в каждом worker.
Общей session fixture на все процессы нет.


## Частые ошибки

| Ошибка | Исправление |
| --- | --- |
| `minversion` подписан как версия Python | Это минимальная версия pytest. Ограничивайте Python метаданными проекта |
| `-k 'not slow'` якобы фильтрует marker | `-k` выбирает по именам/keywords. Для marker используйте `-m` |
| `assert result == result` | Сравните с независимо заданным ожидаемым значением |
| `fixture 'mocker' not found` | Установите pytest-mock именно в тестовое окружение |
| Неизвестный `--json=...` | У pytest нет такого встроенного отчёта. Выберите плагин с документированными флагами |
| Flask использует Django client | Нужна fixture `app.test_client()`; см. [Flask](../../web/flask/testing.md) |
| Обновления библиотек не заметны | Не скрывайте все DeprecationWarning по умолчанию. Фильтруйте конкретную известную причину |


## Источники

- [Запуск](https://docs.pytest.org/en/stable/how-to/usage.html), [фикстуры](https://docs.pytest.org/en/stable/how-to/fixtures.html).
- [Параметризация](https://docs.pytest.org/en/stable/how-to/parametrize.html), [API и конфигурация](https://docs.pytest.org/en/stable/reference/reference.html).
- [Monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html), [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).

[Каталог Python](../../README.md)
