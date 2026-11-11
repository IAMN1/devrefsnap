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
