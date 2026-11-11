from collections.abc import Callable

Listener = Callable[[str], None]


class OrderEvents:
    def __init__(self) -> None:
        self._listeners: list[Listener] = []

    def subscribe(self, listener: Listener) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: Listener) -> None:
        self._listeners.remove(listener)

    def publish(self, event: str) -> None:
        for listener in tuple(self._listeners):
            listener(event)


events = OrderEvents()
calls: list[tuple[str, str]] = []


def update_view(event: str) -> None:
    calls.append(("view", event))


def update_badge(event: str) -> None:
    calls.append(("badge", event))


def broken_listener(event: str) -> None:
    raise RuntimeError("Слушатель недоступен")


events.subscribe(update_view)
events.subscribe(update_badge)
events.publish("order-paid")
assert calls == [("view", "order-paid"), ("badge", "order-paid")]

events.unsubscribe(update_badge)
calls.clear()
events.publish("order-shipped")
assert calls == [("view", "order-shipped")]

# Ошибка второго слушателя не даёт вызвать третьего.
events.subscribe(broken_listener)
events.subscribe(update_badge)
calls.clear()
try:
    events.publish("order-cancelled")
except RuntimeError as error:
    assert str(error) == "Слушатель недоступен"
else:
    raise AssertionError("Ошибка слушателя должна выйти из publish")
assert calls == [("view", "order-cancelled")]
print("OK: observer order, unsubscribe and fail-fast delivery")
