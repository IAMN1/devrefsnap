
# Проверить операции, копии и границы типов

[English](../../../../en/python/language/types/recipes.md)

Запустите пример на Python 3.14, чтобы проверить числа, коллекции и копирование данных. Пример использует стандартную библиотеку и данные в памяти. Синтаксис и объяснения находятся в [карточках типов](README.md).


## Полная программа

Откройте [исходный файл `demo_types.py`](../../../../../examples/python/language/types/demo_types.py). Выполните команду из корня репозитория.

```bash
python3.14 examples/python/language/types/demo_types.py
```


## Результат и границы

Результат — одна строка `types: numbers, collections, conversion errors and copies OK`.
При нарушении показанного свойства выполнение завершится с `AssertionError`.
Пример не измеряет память или скорость.
Запускайте пример без `-O`.
Параметр `-O` отключает assert.

Источники: [стандартные типы](https://docs.python.org/3.14/builtins/stdtypes.html),
[collections](https://docs.python.org/3.14/library/collections.html), [copy](https://docs.python.org/3.14/library/copy.html),
[decimal](https://docs.python.org/3.14/library/decimal.html).
