# Прочитать большой текстовый файл построчно

[Python](../README.md) · [English](../../../en/python/language/read-lines.md)

Если файл слишком велик для загрузки в память целиком, обрабатывайте по одной строке за проход цикла. Нужны Python 3 и текстовый файл в известной кодировке.

Сохраните [готовый пример](../../../../examples/python/language/read-lines.py) как `read-lines.py` в учебном каталоге. Рядом создайте файл `events.txt` в кодировке UTF-8. Оставьте пустую строку между словами.

```text
start

done
```

Программа обходит строки открытого файла.

```python
with open("events.txt", encoding="utf-8") as source:
    for line in source:
        print(line, end="")
```

Из каталога с обоими файлами запустите программу.

```bash
python3 read-lines.py
```

Программа выведет `start`, пустую строку и `done`. Параметр `end=""` сохраняет перевод строки из входного текста без добавления второго. Если файл содержит одну очень длинную строку, эта строка должна поместиться в память. Для файла в другой кодировке укажите её в `encoding`.

[Чтение файлов в Python](https://docs.python.org/3.14/tutorial/inputoutput.html#methods-of-file-objects)
