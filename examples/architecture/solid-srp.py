import json


# До: два независимых повода менять одну функцию.
def invoice_before(quantity: int) -> str:
    return json.dumps({"total": 1200 * quantity})


# После: правило расчёта и формат ответа можно менять отдельно.
def total(quantity: int) -> int:
    return 1200 * quantity


def invoice_json(amount: int) -> str:
    return json.dumps({"total": amount})


assert invoice_json(total(2)) == invoice_before(2) == '{"total": 2400}'
