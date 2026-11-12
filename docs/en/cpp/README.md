# C++

[Catalog](../README.md) · [Русский](../../ru/cpp/README.md)

Use this reference for C++20 programs. Start with one source file or build a project with a library and tests.

| Task | Technique | Example |
| --- | --- | --- |
| Build a first program | `clang++ -std=c++20`, `main` | [First run](#first-run) |
| Choose a type, parameter, or container | `const T&`, `std::vector`, `std::span` | [Syntax and the standard library](syntax.md) |
| Constrain a template or process a range | Concepts, lambdas, `std::ranges` | [Templates](syntax.md#templates) · [Ranges](syntax.md#ranges) |
| Add a dependency and run tests | CMake, vcpkg, GoogleTest, CTest | [Runnable lab](tooling-and-testing.md#run-the-lab) |
| Manage a resource or choose a pattern | RAII, Rule of Zero, Strategy, Adapter | [Practice](practice.md#patterns) |
| Choose a stack and a first project | Libraries and constraints by domain | [Where C++ is used](practice.md#application-areas) |

## First run

Use Clang and a standard library with C++20 support. Run the commands from the repository root in Bash or Zsh. The [complete `basics.cpp` program](../../../examples/cpp/basics.cpp) uses data from the source file.

```bash
build_dir=$(mktemp -d) &&
  clang++ -std=c++20 -Wall -Wextra -pedantic examples/cpp/basics.cpp -o "$build_dir/basics" &&
  "$build_dir/basics"
```

The `-std=c++20` flag selects the language standard. The `clang++` driver compiles the source and links the standard library. Execution starts in `main`. Check the command output.

```text
Count: 2
```

## Types and control flow

In the example, `int` holds a score and `std::size_t` holds the number of matches. The loop `for (int score : scores)` copies each score. The condition `score >= minimum` includes the boundary value. See [types and loops](syntax.md#values).

## Functions

The parameter `const std::vector<int>& scores` gives the function read access without copying the vector. Declare the function before calling it. See [how to choose a parameter type](syntax.md#parameters).

## Collections

This excerpt comes from `main` in the [first example](../../../examples/cpp/basics.cpp). Include `<vector>`.

```cpp
std::vector<int> scores{2, 5};
scores.push_back(3);
```

`scores.size()` returns 3. The vector owns its elements' storage. See [how to choose a container](syntax.md#standard-library).

## Common mistakes

| Symptom | What to check |
| --- | --- |
| The linker reports missing standard library symbols | Use `clang++` to build the program. In a CMake project, check the [target links](tooling-and-testing.md#cmake-targets). |
| An index may be out of bounds | Use `scores.at(i)` to check it. The method throws `std::out_of_range` for an invalid index. |
| An element reference outlived vector reallocation | Reacquire the reference after `push_back` if appending could have increased capacity. See [object lifetimes](practice.md#lifetimes). |

## Sources

- [ISO/IEC 14882:2020 (C++20)](https://www.iso.org/standard/79358.html) · [The WG21 draft's vector specification](https://github.com/cplusplus/draft/blob/n4861/source/containers.tex).
- [C++20 support in Clang](https://clang.llvm.org/cxx_status#cxx20) · [Clang 21 driver](https://releases.llvm.org/21.1.0/tools/clang/docs/CommandGuide/clang.html).
