import pytest
from pydantic import ValidationError

from demo_types import Counter, FrozenPoint, Payload, StrictCount, UserRow, UserView


def test_orm_like_attributes():
    assert UserView.model_validate(UserRow(1, "Alice")).name == "Alice"


def test_assignment_and_frozen():
    counter = Counter(value=1)
    with pytest.raises(ValidationError):
        counter.value = -1
    assert counter.value == 1
    with pytest.raises(ValidationError):
        FrozenPoint(x=1).x = 2
    with pytest.raises(ValidationError):
        StrictCount(count="1")


def test_scalar_types():
    data = dict(user_id=1, url="https://example.com", ip="192.0.2.1",
                uuid="12345678-1234-5678-1234-567812345678", status="active", value=None, score=0.5)
    payload = Payload.model_validate(data)
    assert str(payload.ip) == "192.0.2.1"
    assert "kind" not in payload.model_dump()
    with pytest.raises(ValidationError):
        Payload.model_validate({**data, "score": float("inf")})
