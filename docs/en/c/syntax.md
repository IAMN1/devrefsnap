# C17 syntax and standard library

[C cheat sheet](README.md) · [Русский](../../ru/c/syntax.md)

Use these cards to pick a type, pass data, or find the header for a standard function. The excerpts use C17.

| Task | Technique | Card |
| --- | --- | --- |
| Declare a value and handle a condition | `const`, `if`, `for`, `switch` | [Types and control flow](#types-and-control-flow) |
| Pass a buffer or text | `T *` and length, terminating `'\0'` | [Arrays, strings, and pointers](#arrays-strings-and-pointers) |
| Group fields and pass an operation | `struct`, `enum`, function pointer | [Functions, structs, and callbacks](#functions-structs-and-callbacks) |
| Open a file, convert text, or compare data | `<stdio.h>`, `<stdlib.h>`, `<string.h>` | [Standard library](#standard-library) |
| Allocate memory or return an error | Ownership, output parameter, and cleanup | [Common patterns](practice.md#patterns) |

## Types and control flow

| Task | Type or construct | Condition |
| --- | --- | --- |
| Store an integer or a Boolean flag | `int`, `bool` from `<stdbool.h>` | Check the limits in `<limits.h>` if you need a specific range. |
| Store a size or index | `size_t` from `<stddef.h>` | The type is unsigned. Use `%zu` with `printf`. |
| Store an integer of an exact width | `int32_t`, `uint32_t` from `<stdint.h>` | Exact-width types are available when the implementation supports those representations. |
| Compute a fractional value | `double ratio = 3.0 / 2.0;` | Integer division `3 / 2` gives `1`. |
| Pick an action by condition or code | `if` / `else`, `switch` | In a `switch`, use `break` to exit a `case` branch. |
| Repeat an action | `for`, `while`, `do` / `while` | `do` / `while` checks the condition after running the body. |

Excerpt from the [complete counting program](../../../examples/c/basics.c). The function declares a result and checks every element. The caller passes the number of accessible elements.

```c
#include <stddef.h>

static size_t count_at_least(const int *scores, size_t length, int minimum)
{
    size_t count = 0;
    for (size_t i = 0; i < length; ++i) {
        if (scores[i] >= minimum) {
            ++count;
        }
    }
    return count;
}
```

In `x == y`, the operator compares values. The `=` operator assigns a value. The `&&` and `||` operators may skip evaluation of the right operand. Signed integer overflow causes undefined behavior. Unsigned arithmetic wraps modulo the type's range. Check the range before calculating a buffer size.

## Arrays, strings, and pointers

Excerpt for calling `count_at_least` from the previous card. The call returns `2`.

```c
const int scores[] = {2, 5, 3};
const size_t length = sizeof scores / sizeof scores[0];
const size_t count = count_at_least(scores, length, 3);
```

In the call, the array converts to a pointer to the first element. Pass the element count as a separate argument. In a function parameter list, `int values[]` also declares a pointer type.

| Expression | Action or property |
| --- | --- |
| `&value` | Get the address of an object. |
| `*pointer` | Access the object through a valid pointer. |
| `const int *pointer` | Read an `int` through the pointer. You can assign another address to the pointer. |
| `int *const pointer = &value;` | Fix the address stored in the pointer. You can modify the `int` through it. |
| `char label[] = "ok";` | Create a mutable three-element array that includes `'\0'`. |
| `const char *label = "ok";` | Read a string literal. Modifying the literal causes undefined behavior. |

A string function such as `strlen` requires an accessible terminating `'\0'`. The length from `strlen("ok")` is 2. For an arbitrary buffer, store its byte length separately. In UTF-8 text, the byte count may differ from the character count.

## Functions, structs, and callbacks

A function receives copies of its arguments. Pass an address if it needs to modify an object owned by the caller. The prototype `int run(void);` declares a function with no parameters. A function marked `static` at file scope is available within its [translation unit](tooling-and-testing.md#compile-and-link-files).

Excerpt for visiting sensor readings with a callback. The declarations use `size_t` from `<stddef.h>`.

```c
#include <stddef.h>

struct reading {
    unsigned int sensor;
    double value;
};

typedef void (*reading_fn)(const struct reading *reading, void *context);

static void visit_readings(const struct reading *readings, size_t length,
                           reading_fn visit, void *context)
{
    for (size_t i = 0; i < length; ++i) {
        visit(&readings[i], context);
    }
}
```

Create a value with `struct reading item = {.sensor = 2, .value = 3.5};`. Read the field with `item.value` or `ptr->value`. Pass a valid `visit` pointer and an array with `length` elements. Each call receives the address of a reading and the caller's context. The context and array must remain valid until the traversal finishes. If the callback stores an address, define the required lifetime separately.

Use `enum` for named states. The [port parser](../../../examples/c/port-parser/port.h) returns an `enum port_status`. Define binary formats separately from the in-memory representation of a `struct`. A compiler can insert padding between fields, and byte order depends on the platform.

## Standard library

Include the header before using its API. Check the success condition for each operation according to its contract.

| Task | Header and API | Essential condition |
| --- | --- | --- |
| Print output or read a file | `<stdio.h>` · `printf`, `fopen`, `fgets`, `fclose` | Check the format and return values. If `fgets` returns `NULL`, distinguish end-of-file from an error with `feof` and `ferror`. |
| Convert text to an integer | `<stdlib.h>` · `strtol` | Clear `errno` from `<errno.h>` first. Check for missing digits, trailing characters, `ERANGE`, and the application range. The [port parser](../../../examples/c/port-parser/port.c) validates the string before converting it. |
| Allocate and release memory | `<stdlib.h>` · `malloc`, `realloc`, `free` | Check the size and pointer. Assign an owner that calls `free`. |
| Compare strings or copy bytes | `<string.h>` · `strcmp`, `memcpy`, `memmove` | `strcmp` returns 0 for equal strings. Use `memmove` for overlapping regions. |
| Test for whitespace or convert a letter to lowercase | `<ctype.h>` · `isspace((unsigned char)ch)`, `tolower((unsigned char)ch)` | These calls use a `char ch`. For whitespace, `isspace` returns a nonzero value. When reading with `getchar()`, keep the result in an `int` to distinguish a byte from `EOF`. |
| Check an internal invariant | `<assert.h>` · `assert` | The check disappears under `NDEBUG`. Validate user input with a regular condition. |
| Perform a calculation | `<math.h>` · `sqrt`, `isfinite` | Check the domain. Some Unix toolchains require `-lm` when linking. |

## Sources

- [ISO/IEC 9899:2018 (C17)](https://www.iso.org/standard/74528.html).
- [Public WG14 C11 draft (N1570)](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf), sections 6 and 7 for the core syntax and library.
