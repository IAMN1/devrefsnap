from collections.abc import Callable


# До: новый вид цены требует новой ветки здесь.
def quote_before(quantity: int, kind: str) -> int:
    if kind == "regular":
        return quantity * 1200
    raise ValueError("Неизвестный тариф")


# После: добавление функции тарифа не меняет этого потребителя.
def quote_with(quantity: int, rule: Callable[[int], int]) -> int:
    return rule(quantity)


assert quote_with(2, lambda q: q * 1200) == quote_before(2, "regular") == 2400
assert quote_with(2, lambda q: q * 1000) == 2000
