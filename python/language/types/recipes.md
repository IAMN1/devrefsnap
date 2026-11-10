# Проверить операции, копии и границы типов

Откройте страницу, чтобы выполнить проверки чисел, коллекций и копий на синтетических данных.
Полная программа дополняет [короткие карточки типов](README.md).

[К справочнику типов](README.md)

**Уровень:** базовый → продвинутый.
**Предпосылки:** Python 3.14, стандартная библиотека.

## Полная программа

Сохраните полный пример как `demo_types.py`.
Пример работает с данными в памяти без файлов и сети.

<!-- example: types/demo_types.py -->
```python
import copy
import math
from collections import OrderedDict, defaultdict
from decimal import Decimal, ROUND_HALF_UP


def main():
    assert 0b1010 == 0o12 == 0xA == 10
    assert int("ff", 16) == 255
    assert int(-3.8) == -3
    assert -3.8 // 1 == -4
    assert (3 + 4j).real == 3.0
    assert math.isclose(0.1 + 0.2, 0.3)
    amount = Decimal("2.675").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    assert amount == Decimal("2.68")

    assert bool("False") is True
    assert not any((0, "", [], None))
    assert isinstance(True, int) and type(True) is not int
    try:
        int("abc")
    except ValueError:
        pass
    else:
        raise AssertionError("Ожидался ValueError")

    values = [1, 2]
    values.append(3)
    assert values.pop() == 3
    assert list(range(1, 6, 2)) == [1, 3, 5]
    assert (5,) != 5
    text = "Привет"
    assert text.encode("utf-8").decode("utf-8") == text
    data = bytearray(b"hello")
    data[0] = 72
    assert bytes(data) == b"Hello"
    assert " a b ".strip().split() == ["a", "b"]

    mapping = {"a": 1}
    view = mapping.items()
    mapping["b"] = 2
    assert list(view) == [("a", 1), ("b", 2)]
    assert mapping == {"b": 2, "a": 1}
    grouped = defaultdict(list)
    grouped["python"].append("types")
    assert grouped.get("go") is None and "go" not in grouped
    ordered = OrderedDict(a=1, b=2)
    ordered.move_to_end("a")
    assert list(ordered) == ["b", "a"]

    left, right = {1, 2}, {2, 3}
    assert left | right == {1, 2, 3}
    assert left & right == {2}
    assert left - right == {1}
    assert left ^ right == {1, 3}
    left.discard(99)
    assert {frozenset({1, 2}): "ok"}[frozenset({2, 1})] == "ok"

    original = [[1]]
    alias = original
    shallow = copy.copy(original)
    deep = copy.deepcopy(original)
    original[0].append(2)
    assert alias is original and alias == [[1, 2]]
    assert shallow is not original and shallow == [[1, 2]]
    assert deep == [[1]]
    fixed_container = ([1],)
    fixed_container[0].append(2)
    try:
        hash(fixed_container)
    except TypeError:
        pass
    else:
        raise AssertionError("Кортеж со списком не должен хешироваться")
    rows = [[0] * 2 for _ in range(3)]
    rows[0][0] = 1
    assert rows == [[1, 0], [0, 0], [0, 0]]
    print("types: numbers, collections, conversion errors and copies OK")


if __name__ == "__main__":
    main()
```

## Результат и границы

Запустите `python demo_types.py`.
Результат — одна строка `types: numbers, collections, conversion errors and copies OK`.
При нарушении показанного свойства выполнение завершится с `AssertionError`.
Пример не измеряет память или скорость.
Запускайте пример без `-O`.
Параметр `-O` отключает assert.

Источники: [стандартные типы](https://docs.python.org/3.14/library/stdtypes.html),
[collections](https://docs.python.org/3.14/library/collections.html), [copy](https://docs.python.org/3.14/library/copy.html),
[decimal](https://docs.python.org/3.14/library/decimal.html).
