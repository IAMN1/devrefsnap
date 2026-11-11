from dataclasses import dataclass
from typing import Protocol

from .domain import Product, ProductNotFound


class Catalog(Protocol):
    def get(self, sku: str) -> Product | None:
        ...


@dataclass
class FindProduct:
    catalog: Catalog

    def execute(self, sku: str) -> Product:
        sku = sku.strip()
        if not sku:
            raise ValueError("SKU не должен быть пустым")
        product = self.catalog.get(sku)
        if product is None:
            raise ProductNotFound(sku)
        return product
