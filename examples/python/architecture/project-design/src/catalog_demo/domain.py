from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    sku: str
    title: str


class ProductNotFound(LookupError):
    pass
