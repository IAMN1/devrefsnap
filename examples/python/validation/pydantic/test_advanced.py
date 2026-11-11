import pytest
from pydantic import ValidationError

from demo_advanced import Article, Flexible, Label, Page, user_list
from demo_types import UserView


def test_page_adapter_and_dynamic_model():
    users = user_list.validate_json('[{"id":1,"name":"Alice"}]')
    page = Page[UserView](items=users, total=1, page=1, per_page=10)
    assert page.items[0].id == 1
    assert Label(name="book").weight == 0
    assert Flexible(source="demo").model_dump()["source"] == "demo"
    with pytest.raises(ValidationError):
        user_list.validate_python([{"id": "not-int", "name": "Alice"}])


def test_custom_type_validation_and_schema():
    article = Article(slug="python-guide")
    assert article.model_dump(mode="json") == {"slug": "python-guide"}
    assert Article.model_json_schema()["properties"]["slug"]["type"] == "string"
    with pytest.raises(ValidationError):
        Article(slug="Wrong slug")
