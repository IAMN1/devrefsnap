# Шпаргалка по типам данных в Python

## Содержание
1. [Встроенные типы данных](#встроенные-типы-данных)
2. [Числовые типы](#числовые-типы)
3. [Последовательности](#последовательности)
4. [Строки](#строки)
5. [Словари](#словари)
6. [Множества](#множества)
7. [Булевый тип](#булевый-тип)
8. [NoneType](#nonetype)
9. [Проверка типов](#проверка-типов)
10. [Преобразование типов](#преобразование-типов)

---

## Встроенные типы данных

### Основные категории:
- **Изменяемые (mutable)**: списки, словари, множества
- **Неизменяемые (immutable)**: числа, строки, кортежи, frozenset

---

## Числовые типы

### Целые числа (int)
```python
x = 10
y = -5
z = 0b1010  # двоичная система (10)
w = 0o12    # восьмеричная система (10)
v = 0xA     # шестнадцатеричная система (10)
```

### Числа с плавающей точкой (float)
```python
x = 3.14
y = 2.0
z = -0.5
w = 3e5     # 300000.0
v = 1.5e-3  # 0.0015
```

### Комплексные числа (complex)
```python
x = 3 + 4j
y = complex(2, -3)  # 2 - 3j
print(x.real)       # 3.0
print(x.imag)       # 4.0
```

### Десятичные числа (Decimal)
```python
from decimal import Decimal
x = Decimal('0.1')  # Точное представление
```

---

## Последовательности

### Списки (list) - изменяемые
```python
my_list = [1, 2, 3, 'hello', True]
my_list[0] = 10     # Изменение элемента
my_list.append(4)   # Добавление элемента
my_list.pop()       # Удаление последнего элемента
```

### Кортежи (tuple) - неизменяемые
```python
my_tuple = (1, 2, 3, 'hello')
single_tuple = (5,)  # Кортеж из одного элемента
# my_tuple[0] = 10   # Ошибка! Кортеж неизменяем
```

### Диапазоны (range)
```python
r1 = range(5)        # 0, 1, 2, 3, 4
r2 = range(1, 6)     # 1, 2, 3, 4, 5
r3 = range(1, 10, 2) # 1, 3, 5, 7, 9
```

### Байтовые последовательности (bytes) - неизменяемые
```python
b = b'hello'
# b[0] = 65  # Ошибка!
```

### ByteArray - изменяемые байты
```python
ba = bytearray(b'hello')
ba[0] = 65  # Можно изменять
```

---

## Строки

### Строки (str)
```python
s1 = 'Hello'
s2 = "World"
s3 = '''Многострочная
строка'''
s4 = """Еще одна
многострочная строка"""

# Форматирование строк
name = "Иван"
f_string = f"Привет, {name}"
format_string = "Привет, {}".format(name)
```

### Методы строк
```python
s = "  Hello World  "
s.strip()      # "Hello World"
s.lower()      # "  hello world  "
s.upper()      # "  HELLO WORLD  "
s.split()      # ['Hello', 'World']
s.replace('H', 'J')  # "  Jello World  "
```

---

## Словари

### Словари (dict) - изменяемые
```python
my_dict = {'key1': 'value1', 'key2': 42}
my_dict['key3'] = 3.14      # Добавление
my_dict['key1'] = 'new_val' # Изменение
del my_dict['key2']         # Удаление

# Методы словарей
keys = my_dict.keys()      # Ключи
values = my_dict.values()  # Значения
items = my_dict.items()    # Пары ключ-значение
```

### DefaultDict
```python
from collections import defaultdict
dd = defaultdict(int)  # Значение по умолчанию 0
dd['key'] += 1
```

### OrderedDict
```python
from collections import OrderedDict
od = OrderedDict()
od['a'] = 1
od['b'] = 2
# Сохраняет порядок добавления
```

---

## Множества

### Множества (set) - изменяемые
```python
my_set = {1, 2, 3, 3}  # {1, 2, 3}
my_set.add(4)          # {1, 2, 3, 4}
my_set.remove(2)       # {1, 3, 4}

# Операции
a = {1, 2, 3}
b = {3, 4, 5}
a | b  # Объединение: {1, 2, 3, 4, 5}
a & b  # Пересечение: {3}
a - b  # Разность: {1, 2}
```

### Frozenset - неизменяемые множества
```python
fs = frozenset([1, 2, 3])
# fs.add(4)  # Ошибка!
```

---

## Булевый тип

### Bool (True/False)
```python
x = True
y = False

# Логические операции
a = True and False  # False
b = True or False   # True
c = not True        # False

# Преобразование в bool
bool(0)      # False
bool(1)      # True
bool("")     # False
bool("hi")   # True
bool([])     # False
bool([1])    # True
```

---

## NoneType

### None (отсутствие значения)
```python
x = None
if x is None:
    print("x не имеет значения")
```

---

## Проверка типов

```python
x = 10

type(x)               # <class 'int'>
isinstance(x, int)    # True
isinstance(x, (int, float))  # True

# Проверки для разных типов
isinstance(x, int)    # Для чисел
isinstance(x, str)    # Для строк
isinstance(x, list)   # Для списков
isinstance(x, dict)   # Для словарей
isinstance(x, tuple)  # Для кортежей
isinstance(x, set)    # Для множеств
```

---

## Преобразование типов

```python
# В int
int(3.14)     # 3
int("10")     # 10
int(True)     # 1

# В float
float(5)      # 5.0
float("3.14") # 3.14
float(False)  # 0.0

# В str
str(42)       # "42"
str(3.14)     # "3.14"
str([1, 2])   # "[1, 2]"

# В bool
bool(0)       # False
bool(1)       # True
bool("")      # False
bool("hi")    # True

# В list
list((1, 2))  # [1, 2]
list("abc")   # ['a', 'b', 'c']

# В tuple
tuple([1, 2]) # (1, 2)

# В set
set([1, 2, 2]) # {1, 2}

# В dict (из списка кортежей)
dict([('a', 1), ('b', 2)])  # {'a': 1, 'b': 2}
```

---

## Полезные функции

```python
# Определение типа
print(type(variable))

# Проверка на изменяемость
import sys
sys.getrefcount(variable)  # Количество ссылок

# Размер объекта
sys.getsizeof(variable)

# Копирование
import copy
shallow_copy = copy.copy(original)
deep_copy = copy.deepcopy(original)
```

---

