
# Проверить операции, копии и границы типов

[English](../../../../en/python/language/types/recipes.md)

Откройте страницу, чтобы выполнить проверки чисел, коллекций и копий на синтетических данных.
Полная программа дополняет [короткие карточки типов](README.md).

[К справочнику типов](README.md)

**Уровень:** базовый → продвинутый.
**Предпосылки:** Python 3.14, стандартная библиотека.


## Полная программа

Сохраните полный пример как `demo_types.py`.
Пример работает с данными в памяти без файлов и сети.

[`types/demo_types.py`](../../../../../examples/python/language/types/demo_types.py)


## Результат и границы

Запустите `python demo_types.py`.
Результат — одна строка `types: numbers, collections, conversion errors and copies OK`.
При нарушении показанного свойства выполнение завершится с `AssertionError`.
Пример не измеряет память или скорость.
Запускайте пример без `-O`.
Параметр `-O` отключает assert.

Источники: [стандартные типы](https://docs.python.org/3.14/library/stdtypes.html),
[collections](https://docs.python.org/3.14/library/collections.html), [copy](https://docs.python.org/3.14/library/copy.html),
[decimal](https://docs.python.org/3.14/library/decimal.html).
