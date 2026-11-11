from collections.abc import Callable
from decimal import Decimal, ROUND_CEILING

ShippingRule = Callable[[int], int]


def flat_rate(grams: int) -> int:
    return 500


class LegacyCarrier:
    def quote(self, kilograms: Decimal) -> Decimal:
        return Decimal("3.00") + Decimal("2.00") * kilograms


class CarrierAdapter:
    def __init__(self, carrier: LegacyCarrier):
        self._carrier = carrier

    def __call__(self, grams: int) -> int:
        units = self._carrier.quote(Decimal(grams) / Decimal(1000))
        return int((units * 100).quantize(Decimal("1"), rounding=ROUND_CEILING))


def audited(rule: ShippingRule, events: list[tuple[int, int]]) -> ShippingRule:
    def wrapped(grams: int) -> int:
        result = rule(grams)
        events.append((grams, result))
        return result
    return wrapped


def make_rule(name: str) -> ShippingRule:
    rules = {"flat": flat_rate, "legacy": CarrierAdapter(LegacyCarrier())}
    try:
        return rules[name]
    except KeyError:
        raise ValueError("Неизвестный тариф") from None


def quote_shipping(grams: int, rule: ShippingRule) -> int:
    if type(grams) is not int or grams <= 0:
        raise ValueError("Нужен целый положительный вес")
    result = rule(grams)
    if type(result) is not int or result < 0:
        raise ValueError("Тариф нарушил контракт результата")
    return result


assert quote_shipping(500, make_rule("flat")) == 500
assert quote_shipping(500, make_rule("legacy")) == 400
assert quote_shipping(501, make_rule("legacy")) == 401
events: list[tuple[int, int]] = []
assert quote_shipping(500, audited(make_rule("legacy"), events)) == 400
assert events == [(500, 400)]
for operation in [
    lambda: quote_shipping(0, flat_rate),
    lambda: quote_shipping(1, lambda _: -1),
    lambda: make_rule("unknown"),
]:
    try:
        operation()
    except ValueError:
        pass
    else:
        raise AssertionError("Ожидался отказ входа/контракта/выбора")
print("OK: strategies, unit adapter, rounding, wrapper and factory refusal")
