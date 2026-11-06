# Проверять инварианты и контракты

Два полных локальных примера: резерв остатка и подстановка источника цен.
Используйте, когда нужно проверить отказ без изменения состояния или заменить реализацию по общему контракту.

| Задача | Сценарий | Что проверяет |
| --- | --- | --- |
| Защитить остаток | [Stock](#резерв-остатка) | Успех, неверный вход, нехватка, сохранение состояния при отказе |
| Заменить источник цены | [PriceReader](#подстановка-источника-цен) | Результат, KeyError, повторное чтение; обнаружение несовместимой реализации |

[К принципам](principles.md#контракт-и-инвариант) · [К SOLID](solid.md) · [К архитектуре](README.md)

**Уровень:** средний — инварианты; продвинутый — семантика подстановки.
**Предпосылки:** функции, классы, исключения, assert и структурная типизация Python.

| Проверка | Дата и основание |
| --- | --- |
| Сверено с документацией | 2026-11-06: Python 3.14, PEP 544; первичные источники внизу |
| Выполнено | 2026-11-06: Python 3.14.7, оба полных примера; сценарии перечислены ниже |
| Границы | Память, один поток, синтетические данные; без БД, сети и статического анализатора |

## Резерв остатка

**Средний уровень.** Контракт: начальный остаток — целое неотрицательное число;
резерв — целое положительное число; при отказе остаток сохраняется.
`bool` намеренно не принимается как количество, хотя это подкласс `int` в Python.

Полный пример. Сохраните как `invariants.py`, выполните `python3.14 invariants.py`; зависимостей нет.

<!-- example: architecture/invariants.py -->
```python
class OutOfStock(Exception):
    pass


class Stock:
    def __init__(self, available: int):
        if type(available) is not int or available < 0:
            raise ValueError("Остаток должен быть целым неотрицательным числом")
        self._available = available

    @property
    def available(self) -> int:
        return self._available

    def reserve(self, quantity: int) -> None:
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Нужно целое положительное количество")
        if quantity > self._available:
            raise OutOfStock(quantity)
        self._available -= quantity


stock = Stock(3)
stock.reserve(2)
assert stock.available == 1
for quantity, expected in [(0, ValueError), (True, ValueError), (2, OutOfStock)]:
    before = stock.available
    try:
        stock.reserve(quantity)
    except expected:
        pass
    else:
        raise AssertionError("Ожидался отказ контракта")
    assert stock.available == before
try:
    Stock(-1)
except ValueError:
    pass
else:
    raise AssertionError("Недопустимое начальное состояние")
print("OK: successful reservation, invariant and unchanged state on refusal")
```

**Результат:** `OK: successful reservation, invariant and unchanged state on refusal`.
Проверены успешный резерв, `0`, `True`, нехватка и недопустимый начальный остаток.

`_available` — соглашение о внутреннем API, а не защита от намеренного доступа.
Возврат изменяемой коллекции тоже может открыть обход инварианта: выбирайте копию,
неизменяемое представление или явную операцию по требованиям.
Конкурентный резерв в БД потребует отдельной транзакции/протокола; этот пример его не проверяет.

## Подстановка источника цен

**Продвинутый уровень.** Контракт снимка цен: известный `book` имеет неотрицательную целую цену
в условных центах; неизвестный `sku` вызывает `KeyError`; повторное чтение снимка сохраняет цену.
`quote` принимает целое положительное количество. Это договорённость потребителя, не только сигнатура.

Полный пример. Сохраните как `solid-contract.py`, выполните `python3.14 solid-contract.py`; pip не нужен.

<!-- example: architecture/solid-contract.py -->
```python
from typing import Protocol


class PriceReader(Protocol):
    def price(self, sku: str) -> int: ...


class SnapshotPrices:
    def __init__(self, prices: dict[str, int]):
        if any(type(value) is not int or value < 0 for value in prices.values()):
            raise ValueError("Цена должна быть целой и неотрицательной")
        self._prices = dict(prices)

    def price(self, sku: str) -> int:
        return self._prices[sku]


class SilentMissingPrices:
    # Форма метода совпала, но неизвестный sku скрывается вместо KeyError.
    def price(self, sku: str) -> int:
        return {"book": 1200}.get(sku, 0)


def quote(reader: PriceReader, sku: str, quantity: int) -> int:
    if type(quantity) is not int or quantity <= 0:
        raise ValueError("Количество должно быть целым положительным")
    return reader.price(sku) * quantity


def check_reader_contract(reader: PriceReader) -> None:
    value = reader.price("book")
    assert type(value) is int and value >= 0
    assert reader.price("book") == value
    try:
        reader.price("missing")
    except KeyError:
        pass
    else:
        raise AssertionError("Реализация скрыла неизвестный sku")


reader = SnapshotPrices({"book": 1200})
check_reader_contract(reader)
assert quote(reader, "book", 2) == 2400
try:
    quote(reader, "book", 0)
except ValueError:
    pass
else:
    raise AssertionError("Ожидался отказ для количества 0")
try:
    check_reader_contract(SilentMissingPrices())
except AssertionError as error:
    assert "sku" in str(error)
else:
    raise AssertionError("Контракт должен обнаружить несовместимую реализацию")
print("OK: consumer contract, valid substitution and incompatible implementation detected")
```

**Результат:** `OK: consumer contract, valid substitution and incompatible implementation detected`.
Проверены цена `2400`, отказ количества `0`, успешная подстановка и обнаружение неправильной ошибки.

`Protocol` описывает структурную типизацию для статической проверки. Аннотации не проверяют
договорённость автоматически при запуске; `runtime_checkable` проверяет наличие атрибутов,
а не семантику и сигнатуры методов. Здесь выполнены поведенческие проверки, статический анализатор не запускался.
Конечный набор проверок не доказывает подстановочность для всех входов и реализаций.

### Возможное размещение по модулям

Это схема исходников для выросшего примера, а не набор файлов, необходимый для запуска кода выше.
В одном коротком скрипте роли можно оставить рядом.

```text
pricing/
├── contracts.py   # PriceReader: контракт, нужный потребителю
├── quote.py       # quote: правило расчёта, импортирует PriceReader
├── snapshot.py    # SnapshotPrices: локальный источник
└── main.py        # сборка: создаёт SnapshotPrices и передаёт в quote
```

На [схеме DIP](solid.md#d--направление-зависимости-di--способ-передачи) отдельно показаны
зависимости кода. Вызов `reader.price()` идёт к переданному объекту без импорта его класса внутри `quote`.
Для замены снимка реальной БД согласуйте ошибки, транзакции, `NULL` и свежесть данных.
Снимок и «всегда последняя цена» — разные контракты.

## Источники

- [Python 3.14: Protocol](https://docs.python.org/3.14/library/typing.html#typing.Protocol), [PEP 544](https://peps.python.org/pep-0544/) — структурная типизация и границы runtime-проверки.
- [Liskov / Wing: A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf) — поведенческий контракт.
- [Robert C. Martin: SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — причины изменений.
