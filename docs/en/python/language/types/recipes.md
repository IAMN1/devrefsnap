<a id="проверить-операции-копии-и-границы-типов"></a>
# Check operations, copies, and type boundaries

[Русский](../../../../ru/python/language/types/recipes.md)

Use this page to check numbers, collections, and copies with synthetic data.
The complete program complements the [short type cards](README.md).

[Type reference](README.md)

The exercise ranges from basic to advanced. You need Python 3.14 and the standard library.

<a id="полная-программа"></a>
## Complete program

Save the complete example as `demo_types.py`.
The program uses in-memory data and requires no files or network connection.

[`types/demo_types.py`](../../../../../examples/python/language/types/demo_types.py)

<a id="результат-и-границы"></a>
## Result and limits

Run `python demo_types.py`.
Expect one line, `types: numbers, collections, conversion errors and copies OK`.
If a demonstrated property fails, the program raises `AssertionError`.
The exercise checks behavior. Measure memory or speed separately.
Run the program with assertions enabled. The `-O` option disables them.

Sources include [built-in types](https://docs.python.org/3.14/library/stdtypes.html),
[collections](https://docs.python.org/3.14/library/collections.html), [copy](https://docs.python.org/3.14/library/copy.html),
and [decimal](https://docs.python.org/3.14/library/decimal.html).
