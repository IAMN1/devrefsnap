# Фикстуры, данные и assertions

Откройте страницу, чтобы проверить результат функции, ожидаемую ошибку и очистку ресурсов.
Полный набор использует SQLite в памяти и временные файлы.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Проверить результат и неверный ввод | `parametrize`, `approx`, `raises` | [Полный набор](#полный-учебный-пример) |
| Выдать ресурс и закрыть его | Фикстура с `yield` и `finally` | [Полный набор](#полный-учебный-пример) |
| Выбрать время жизни данных | Scope и fixture-фабрика | [Область действия](#область-действия-и-фабрики) |
| Перебрать независимые варианты | Несколько `parametrize` | [Декартово произведение](#параметризовать-независимые-измерения) |

Уровень: базовый и средний.
Предпосылки: Python 3.14.7 и pytest 9.2.0 для воспроизведения примеров.
[К справочнику pytest](README.md).

## Полный учебный пример

Создайте два файла ниже в одном временном каталоге.
Зависимость: pytest.
SQLite входит в стандартную библиотеку Python.
Из активированного отдельного окружения выполните `python -m pytest -q test_basics.py`.
Пример работает только с БД в памяти и временными файлами.

<!-- example: pytest/demo_service.py -->
```python
import asyncio


def subtotal(quantity: int, price: float) -> float:
    if type(quantity) is not int or quantity < 0:
        raise ValueError("quantity must be a non-negative integer")
    return quantity * price


def read_remote(order_id: int) -> dict:
    raise RuntimeError("external adapter is not configured in this demo")


def status_label(order_id: int) -> str:
    payload = read_remote(order_id)
    return f"order {order_id}: {payload['status']}"


async def uppercase(value: str) -> str:
    await asyncio.sleep(0)
    return value.upper()
```

<!-- example: pytest/test_basics.py -->
```python
import sqlite3
import warnings

import pytest

from demo_service import subtotal


@pytest.fixture
def connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE items (name TEXT NOT NULL)")
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(params=["utf-8", "utf-16"])
def encoding(request):
    return request.param


@pytest.mark.parametrize("quantity, price, expected", [
    (0, 2.5, 0.0),
    (1, 2.5, 2.5),
    (3, 2.5, 7.5),
])
def test_subtotal(quantity, price, expected):
    assert subtotal(quantity, price) == pytest.approx(expected)


@pytest.mark.parametrize("quantity", [-1, 1.5, True])
def test_invalid_quantity(quantity):
    with pytest.raises(ValueError, match="quantity") as error:
        subtotal(quantity, 2.5)
    assert "non-negative integer" in str(error.value)


def test_database_write(connection):
    connection.execute("INSERT INTO items VALUES (?)", ("apple",))
    assert connection.execute("SELECT name FROM items").fetchall() == [("apple",)]


def test_database_starts_empty(connection):
    assert connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_file_roundtrip(tmp_path, encoding):
    path = tmp_path / "note.txt"
    path.write_text("Привет", encoding=encoding)
    assert path.read_text(encoding=encoding) == "Привет"


def test_print_output(capsys):
    print("ready")
    assert capsys.readouterr().out == "ready\n"


def test_float_sum():
    assert 0.1 + 0.2 == pytest.approx(0.3, rel=1e-9)


def test_warning():
    with pytest.warns(UserWarning, match="old format"):
        warnings.warn("old format", UserWarning)
```

Ожидается **13 passed**.
Тесты проверяют корректные и ошибочные количества.
Тесты также проверяют SQL, изоляцию fixture между тестами, два encoding, вывод и предупреждение.
Сравнение `0.1 + 0.2 == 0.3` обычно ложно для Python float.
Выбирайте допуск по смыслу данных.
Не подбирайте допуск ради прохождения любого теста.
Для денежных сумм отдельно рассмотрите Decimal или целые минимальные единицы.

## Область действия и фабрики

| Scope | Когда создаётся значение |
| --- | --- |
| `function` | Для каждого тестового вызова; значение по умолчанию |
| `class` | В рамках тестового класса |
| `module` | В рамках модуля |
| `package` | В рамках пакета |
| `session` | В рамках сессии конкретного процесса pytest |

Нельзя передавать function-scoped ресурс в session-scoped fixture без изменения дизайна.
pytest сообщает ScopeMismatch.
`autouse=True` делает fixture неявной для тестов своей области.
Используйте `autouse=True` для действительно общей обязательной подготовки.
Размещайте общие fixture в `conftest.py`.
Избегайте ненужных импортов тяжёлых зависимостей.

Фрагмент fixture-фабрики подходит для произвольного тестового файла.
Фрагмент требует `import pytest`:

```python
@pytest.fixture
def user_factory():
    def build(**overrides):
        data = {"username": "alice", "is_active": True}
        data.update(overrides)
        return data
    return build
```

В тесте `user_factory(username="bob")` создаёт независимые данные.
Если вы проверяете валидацию модели, не заменяйте реальную валидацию такой фабрикой.

## Параметризовать независимые измерения

Стекирование двух `parametrize` даёт декартово произведение вариантов, а не zip.
Каждому варианту нужен осмысленный ожидаемый результат.
Можно задать `ids` и отдельные `pytest.param(..., marks=...)`.
Для дорогой подготовки используйте параметризованную fixture или indirect-передачу параметра.
Не делайте реальный сетевой запрос только ради перебора входов.

## Источники

[Fixture scopes и teardown](https://docs.pytest.org/en/stable/how-to/fixtures.html),
[parametrize](https://docs.pytest.org/en/stable/how-to/parametrize.html),
[assertions](https://docs.pytest.org/en/stable/how-to/assert.html).
