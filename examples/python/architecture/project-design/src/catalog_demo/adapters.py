import sqlite3

from .domain import Product


class MemoryCatalog:
    def __init__(self, products: list[Product]):
        self._products = {product.sku: product for product in products}

    def get(self, sku: str) -> Product | None:
        return self._products.get(sku)


class SQLiteCatalog:
    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def get(self, sku: str) -> Product | None:
        row = self._connection.execute(
            "SELECT sku, title FROM products WHERE sku = ?", (sku,)
        ).fetchone()
        return Product(*row) if row is not None else None
