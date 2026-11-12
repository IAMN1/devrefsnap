<a id="проверить-операции-копии-и-границы-типов"></a>
# Check operations, copies, and type boundaries

[Русский](../../../../ru/python/language/types/recipes.md)

Run the example with Python 3.14 to check numbers, collections, and copying. It uses the standard library and in-memory data. See the [type cards](README.md) for syntax and explanations.

<a id="полная-программа"></a>
## Complete program

Open the [`demo_types.py` source file](../../../../../examples/python/language/types/demo_types.py). Run this command from the repository root.

```bash
python3.14 examples/python/language/types/demo_types.py
```

<a id="результат-и-границы"></a>
## Result and limits

Expect one line, `types: numbers, collections, conversion errors and copies OK`.
If a demonstrated property fails, the program raises `AssertionError`.
The exercise checks behavior. Measure memory or speed separately.
Run the program with assertions enabled. The `-O` option disables them.

Sources include [built-in types](https://docs.python.org/3.14/builtins/stdtypes.html),
[collections](https://docs.python.org/3.14/library/collections.html), [copy](https://docs.python.org/3.14/library/copy.html),
and [decimal](https://docs.python.org/3.14/library/decimal.html).
