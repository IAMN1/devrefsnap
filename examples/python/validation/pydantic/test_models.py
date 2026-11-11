from decimal import Decimal

import pytest
from pydantic import ValidationError

from demo_models import Product, PublicUser, Tree, UserInput


def test_alias_and_public_output():
    user = UserInput(id="1", fullName=" Alice Doe ", email="alice@example.com", password="training-password")
    assert user.id == 1
    assert user.full_name == "Alice Doe"
    assert "password" not in user.model_dump()
    assert PublicUser.model_validate(user.model_dump()).model_dump(by_alias=True)["fullName"] == "Alice Doe"


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValidationError):
        PublicUser(id=1, fullName="Alice", email="alice@example.com", created_at="2026-11-06T12:00:00")


def test_offset_timestamp_serializes_in_utc():
    user = PublicUser(id=1, fullName="Alice", email="alice@example.com", created_at="2026-11-06T12:00:00+03:00")
    assert user.model_dump(mode="json")["created_at"] == "2026-11-06T09:00:00Z"


@pytest.mark.parametrize("patch", [{"id": 0}, {"email": "bad"}, {"role": "root"}, {"extra": 1}])
def test_invalid_user(patch):
    data = {"id": 1, "fullName": "Alice", "email": "alice@example.com", **patch}
    with pytest.raises(ValidationError):
        PublicUser.model_validate(data)


def test_zero_discount_and_json_roundtrip():
    product = Product(name="Book", price="10.00", discount_price="0")
    assert product.final_price == Decimal("0")
    assert Product.model_validate_json(product.model_dump_json()).final_price == Decimal("0")


@pytest.mark.parametrize("price,discount", [("10", "10"), ("0", None), ("Infinity", None), ("NaN", None)])
def test_invalid_product(price, discount):
    with pytest.raises(ValidationError):
        Product(name="Book", price=price, discount_price=discount)


def test_recursive_model_and_independent_lists():
    first = Tree(name="root", children=[{"name": "leaf"}])
    second = Tree(name="other")
    assert first.children[0].name == "leaf"
    assert second.children == []
