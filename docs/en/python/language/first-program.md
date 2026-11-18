# Your first Python program

[Русский](../../../ru/python/language/first-program.md) · [Python section](../README.md)

Calculate the cost of three tickets at 50 rubles each. If your computer does not have Python 3 yet, [install Python](https://www.python.org/downloads/).

## Run the program

Save these three lines in a file named `tickets.py` in a folder of your choice. You can also download the [complete file](../../../../examples/python/language/tickets.py).

```python
ticket_price = 50
tickets = 3
print(ticket_price * tickets)
```

Open a terminal in the folder that contains the file. Run this command.

```bash
python3 tickets.py
```

On Windows with the Python launcher installed, use `py tickets.py`.

The program prints `150`. The first line sets the ticket price and the second sets the number of tickets. The `*` operator multiplies the two values. The `print()` function displays the result.

## Change one number

Change `tickets = 3` to `tickets = 4`. What number will the program print now? Save the file and run the same command again.

<details>
<summary>Check your prediction</summary>

The program prints `200`. Each ticket still costs 50 rubles, and there are now four tickets.

</details>

Next, try [removing duplicates from a list of languages](types/README.md#collections).
