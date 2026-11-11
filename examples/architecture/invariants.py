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
