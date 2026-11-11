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
