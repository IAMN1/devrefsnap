import logging

from .adapters import MemoryCatalog
from .application import FindProduct
from .config import Settings
from .domain import Product


def build_application(settings: Settings) -> FindProduct:
    logging.basicConfig(level=settings.log_level, format="%(levelname)s %(message)s")
    catalog = MemoryCatalog([Product("book", "Python guide")])
    return FindProduct(catalog)
