from dataclasses import dataclass


@dataclass(frozen=True)
class ReserveStock:
    sku: str
    quantity: int
    request_id: str


class ReserveStockHandler:
    def __init__(self, stock: dict[str, int]) -> None:
        self.stock = dict(stock)
        self._completed: dict[str, tuple[ReserveStock, int]] = {}

    def __call__(self, command: ReserveStock) -> int:
        if not isinstance(command.sku, str) or not command.sku:
            raise ValueError("Нужен SKU")
        if type(command.quantity) is not int or command.quantity <= 0:
            raise ValueError("Нужно целое положительное количество")
        if not isinstance(command.request_id, str) or not command.request_id:
            raise ValueError("Нужен request_id")
        if command.request_id in self._completed:
            previous, result = self._completed[command.request_id]
            if previous != command:
                raise ValueError("request_id уже использован с другими параметрами")
            return result
        available = self.stock.get(command.sku, 0)
        if available < command.quantity:
            raise ValueError("Недостаточно товара")
        remaining = available - command.quantity
        self.stock[command.sku] = remaining
        self._completed[command.request_id] = (command, remaining)
        return remaining


handler = ReserveStockHandler({"book": 3})
command = ReserveStock("book", 1, "request-1")
assert handler(command) == 2
assert handler(command) == 2  # Успешный повтор не резервирует ещё раз.
assert handler.stock == {"book": 2}

for invalid in [
    ReserveStock("book", 0, "request-2"),
    ReserveStock("book", 4, "request-3"),
    ReserveStock("book", 2, "request-1"),
]:
    try:
        handler(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("Ожидался отказ валидации/остатка/конфликта ID")
    assert handler.stock == {"book": 2}
print("OK: command validation, reserve, replay and ID conflict")
