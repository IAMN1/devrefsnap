# C

[Catalog](../README.md) · [Русский](../../ru/c/README.md)

Build your first C17 program or look up a technique for an existing project. The examples use a hosted environment with a compiler and the C standard library. For firmware and kernel modules, use the target platform's toolchain.

| Task | Technique | Example |
| --- | --- | --- |
| Build and run a program | `clang -std=c17`, `main` | [First run](#first-run) |
| Look up syntax or a standard library function | Types, loops, strings, structs, headers | [Syntax and standard library](syntax.md) |
| Pass an array to a function | Pointer and element count | [Arrays and memory](#arrays-and-memory) |
| Build multiple files and add a dependency | CMake, `FetchContent` | [Builds and dependencies](tooling-and-testing.md#packages) |
| Check success, boundaries, and failures | CTest, Unity | [Port parser tests](tooling-and-testing.md#tests) |
| Document memory or resource ownership | `create`/`destroy`, shared cleanup | [Patterns](practice.md#patterns) |
| Pick tools for a project | Platform, libraries, constraints | [Application areas](practice.md#application-areas) |

## First run

Use Clang with C17 support and the C standard library. The commands use Bash or Zsh.

From the repository root, build and run the [complete `basics.c` program](../../../examples/c/basics.c). The program uses the array in the source file.

```bash
build_dir=$(mktemp -d) &&
  clang -std=c17 -Wall -Wextra -pedantic examples/c/basics.c -o "$build_dir/basics" &&
  "$build_dir/basics"
```

The flag `-std=c17` selects the language standard. The flags `-Wall`, `-Wextra`, and `-pedantic` enable additional warnings. Execution starts in `main`. The statement `return 0` signals successful completion.

```text
Count: 2
```

## Types and control flow

The program uses `int` for array values and `size_t` for the length and index. If the length is zero, the function skips the loop and returns 0. The `if` condition includes values equal to the threshold. See [types and control flow](syntax.md#types-and-control-flow).

## Functions

Declare a function before calling it. The function `count_at_least` receives copies of the pointer, length, and threshold. See [functions, structs, and callbacks](syntax.md#functions-structs-and-callbacks).

## Arrays and memory

Calculate the length with `sizeof scores / sizeof scores[0]` where `scores` is declared as an array. Pass a pointer to the first element and the length. See [arrays, strings, and pointers](syntax.md#arrays-strings-and-pointers).

## Common mistakes

| Mistake | What to do |
| --- | --- |
| Accessing `scores[length]` | Check `i < length` before reading. Out-of-bounds access causes undefined behavior. |
| Using `sizeof scores` to find the length inside the function | Use the `length` parameter. In the function, `sizeof scores` gives the size of the pointer in bytes. |
| Returning a pointer to a local array | Pass a caller-owned buffer and its capacity. The function writes to that buffer, which remains available after the call. See [resource ownership](practice.md#patterns). |
| Printing a `size_t` with `%d` | Use `%zu` with `printf`. |

## Sources

- [ISO/IEC 9899:2018 (C17)](https://www.iso.org/standard/74528.html).
- [C language modes in Clang 21](https://releases.llvm.org/21.1.0/tools/clang/docs/UsersManual.html#differences-between-various-standard-modes) and [compile and link commands](https://releases.llvm.org/21.1.0/tools/clang/docs/CommandGuide/clang.html).
