# Проверять инварианты и контракты

Страница содержит два полных локальных примера.
Первый пример резервирует остаток.
Второй пример подставляет источник цен.
Используйте примеры для проверки отказа без изменения состояния или замены реализации по общему контракту.

| Задача | Сценарий | Что проверяет |
| --- | --- | --- |
| Защитить остаток | [Stock](#резерв-остатка) | Успех, неверный вход, нехватка, сохранение состояния при отказе |
| Заменить источник цены | [PriceReader](#подстановка-источника-цен) | Результат, KeyError, повторное чтение; обнаружение несовместимой реализации |

[К принципам](principles.md#контракт-и-инвариант) · [К SOLID](solid.md) · [К архитектуре](README.md)

**Уровень:** средний для инвариантов.
Продвинутый уровень разбирает семантику подстановки.
**Предпосылки:** функции, классы, исключения, assert и структурная типизация Python.

Примеры используют Python 3.14 и синтетические данные в памяти.
Примеры выполняются в одном потоке без БД и сети.

## Резерв остатка

**Средний уровень.** Начальный остаток должен быть целым неотрицательным числом.
Количество для резерва должно быть целым положительным числом.
При отказе остаток не меняется.
`bool` намеренно недопустим как количество, хотя Python считает `bool` подклассом `int`.

Полный пример не требует зависимостей.
Сохраните код как `invariants.py`.
Выполните `python3.14 invariants.py`.

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
Пример включает успешный резерв и отказы для `0`, `True`, нехватки и недопустимого начального остатка.

`_available` обозначает соглашение о внутреннем API.
Имя поля не защищает от намеренного доступа.
Возврат изменяемой коллекции тоже может открыть обход инварианта.
Выберите копию, неизменяемое представление или явную операцию по требованиям.
Для конкурентного резерва в БД потребуется отдельная транзакция или протокол.

## Подстановка источника цен

**Продвинутый уровень.** Контракт снимка задаёт цену известного `book` целым неотрицательным числом в условных центах.
Неизвестный `sku` вызывает `KeyError`.
Повторное чтение снимка сохраняет цену.
`quote` принимает целое положительное количество.
Контракт задаёт договорённость потребителя, а не только сигнатуру.

Полный пример не требует pip.
Сохраните код как `solid-contract.py`.
Выполните `python3.14 solid-contract.py`.

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
Пример включает цену `2400`, отказ количества `0`, успешную подстановку и обнаружение неправильной ошибки.

`Protocol` описывает структурную типизацию для статической проверки.
Аннотации не проверяют договорённость автоматически при запуске.
`runtime_checkable` проверяет наличие атрибутов.
Он не проверяет семантику и сигнатуры методов.
Пример сравнивает поведение реализаций при запуске.
Для проверки типов используйте отдельный статический анализатор.
Конечный набор проверок не доказывает подстановочность для всех входов и реализаций.

### Возможное размещение по модулям

Дерево показывает возможные исходники для выросшего примера.
Эти файлы не нужны для запуска кода выше.
В коротком скрипте роли можно оставить рядом.

```text
pricing/
├── contracts.py   # PriceReader: контракт, нужный потребителю
├── quote.py       # quote: правило расчёта, импортирует PriceReader
├── snapshot.py    # SnapshotPrices: локальный источник
└── main.py        # сборка: создаёт SnapshotPrices и передаёт в quote
```

На [схеме DIP](solid.md#d--направление-зависимости-di--способ-передачи) отдельно показаны зависимости кода.
`reader.price()` вызывает метод переданного объекта.
Для этого вызова `quote` не должен импортировать класс объекта.
При замене снимка реальной БД согласуйте ошибки.
Согласуйте транзакции, `NULL` и свежесть данных.
Снимок и «всегда последняя цена» задают разные контракты.

## Источники

- [Python 3.14: Protocol](https://docs.python.org/3.14/library/typing.html#typing.Protocol), [PEP 544](https://peps.python.org/pep-0544/) — структурная типизация и границы runtime-проверки.
- [Liskov / Wing: A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf) — поведенческий контракт.
- [Robert C. Martin: SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — причины изменений.
