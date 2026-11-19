# Read a large text file line by line

[Python](../README.md) · [Русский](../../../ru/python/language/read-lines.md)

If a file is too large to load into memory, process one line at a time. You need Python 3 and a text file with a known encoding.

Save the [complete example](../../../../examples/python/language/read-lines.py) as `read-lines.py` in a practice directory. Next to it, create a UTF-8 file named `events.txt`. Leave a blank line between the words.

```text
start

done
```

The program iterates over the open file.

```python
with open("events.txt", encoding="utf-8") as source:
    for line in source:
        print(line, end="")
```

From the directory containing both files, run the program.

```bash
python3 read-lines.py
```

The program prints `start`, a blank line, and `done`. The `end=""` argument keeps `print` from adding a second line ending. If the file contains one very long line, that line must fit in memory. If the file uses a different encoding, set `encoding` accordingly.

[Reading files in Python](https://docs.python.org/3.14/tutorial/inputoutput.html#methods-of-file-objects)
