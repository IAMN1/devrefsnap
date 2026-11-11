import argparse

from .bootstrap import build_application
from .config import Settings
from .domain import ProductNotFound


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sku")
    args = parser.parse_args()
    application = build_application(Settings())
    try:
        product = application.execute(args.sku)
    except (ValueError, ProductNotFound):
        parser.error("Товар не найден или SKU пуст")
    print(f"{product.sku}: {product.title}")


if __name__ == "__main__":
    main()
