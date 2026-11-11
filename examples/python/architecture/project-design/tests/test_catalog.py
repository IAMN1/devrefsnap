from contextlib import closing
import sqlite3

import pytest
from pydantic import ValidationError

from catalog_demo.adapters import MemoryCatalog, SQLiteCatalog
from catalog_demo.application import FindProduct
from catalog_demo.config import Settings
from catalog_demo.domain import Product, ProductNotFound


@pytest.fixture(params=["memory", "sqlite"])
def catalog(request):
    if request.param == "memory":
        yield MemoryCatalog([Product("book", "Python guide")])
    else:
        with closing(sqlite3.connect(":memory:")) as connection:
            with connection:
                connection.execute("CREATE TABLE products (sku TEXT PRIMARY KEY, title TEXT NOT NULL)")
                connection.execute("INSERT INTO products VALUES (?, ?)", ("book", "Python guide"))
            yield SQLiteCatalog(connection)


def test_existing_product(catalog):
    assert FindProduct(catalog).execute(" book ") == Product("book", "Python guide")


@pytest.mark.parametrize("sku", ["unknown", "book' OR 1=1 --"])
def test_unknown_product(catalog, sku):
    with pytest.raises(ProductNotFound):
        FindProduct(catalog).execute(sku)


def test_empty_sku(catalog):
    with pytest.raises(ValueError, match="SKU"):
        FindProduct(catalog).execute(" ")


def test_settings_are_validated(monkeypatch):
    monkeypatch.setenv("CATALOG_DEMO_ENVIRONMENT", "test")
    assert Settings().environment == "test"
    with pytest.raises(ValidationError):
        Settings(environment="unrecognized")
