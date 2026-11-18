# C++20 syntax and the standard library

[C++ reference](README.md) · [Русский](../../ru/cpp/syntax.md)

Use these cards to choose a type, pass an argument, and process a sequence. The snippets require a compiler and standard library that support the C++20 features in use.

| Task | Technique | Example |
| --- | --- | --- |
| Initialize values and loop over a collection | `auto`, `const`, range-based loop | [Values and loops](#values) |
| Accept a value, reference, or view | `T`, `const T&`, `std::span` | [Parameters](#parameters) |
| Enforce an object invariant | Constructor, `private`, `const` member function | [Classes](#classes) |
| Use one operation for multiple types | Function template, `std::integral` | [Templates](#templates) |
| Select elements | Lambda, `std::ranges::count_if`, `std::views::filter` | [Ranges](#ranges) |
| Choose a container, I/O API, or synchronization primitive | Standard library headers | [Standard library](#standard-library) |
| Signal absence or an error | `std::optional`, exception, error code | [Errors](#errors) |

<a id="values"></a>

## Values and loops

Use `int` for small integers, `double` for approximate arithmetic, and `bool` for conditions. Initialize local variables at declaration. The `auto` keyword deduces the type from the expression and preserves static typing.

Function body excerpt. Include `<cstddef>` and `<vector>`.

```cpp
const std::vector<int> scores{55, 60, 95};
const auto minimum = 60;
std::size_t count{};
for (int score : scores) {
    if (score >= minimum) {
        ++count;
    }
}
```

Here `minimum` has type `const int`. The loop copies one `int` at a time and `count` becomes 2. Use `const auto&` to read elements that are expensive to copy. Use `auto&` to modify elements of a mutable collection. [Complete first example](../../../examples/cpp/basics.cpp).

<a id="parameters"></a>

## Values, references, and `const`

| Function intent | Parameter type | Condition |
| --- | --- | --- |
| Receive a small value | `int value`, `bool flag` | The function receives its own value. |
| Read an object that is expensive to copy | `const T& value` | The function reads through the reference. |
| Modify the caller's object | `T& value` | Pass a mutable object. |
| Accept the address of an optional object | `const T* value` | Check for `nullptr` before dereferencing. |
| Read a contiguous sequence | `std::span<const int> values` | The element storage must stay available. |
| Take ownership of a resource | `std::unique_ptr<T> resource` | The call transfers ownership. |

`const T*` restricts mutation of the object through that pointer. `T* const` prevents reseating the pointer. `const T&` restricts mutation through that reference. `auto copy = value` normally creates a value, while `auto& alias = value` binds a name to an existing object.

Declaration excerpt. Include `<span>`. `ScoreSummary` is the two-counter structure from the [lab header](../../../examples/cpp/score-summary.hpp).

```cpp
ScoreSummary summarize_scores(std::span<const int> scores, int minimum);
```

Pass an array or a vector of `int`. The function accepts a view and returns two counters by value. The [implementation](../../../examples/cpp/score-summary.cpp) uses the view only during the call.

<a id="classes"></a>

## Classes and invariants

Keep a field `private` if the constructor and methods must preserve valid state. Mark a read-only method `const`.

Class definition excerpt. Include `<stdexcept>`.

```cpp
class ScoreLimit {
public:
    explicit ScoreLimit(int value) : value_{value}
    {
        if (value < 0 || value > 100) {
            throw std::invalid_argument{"limit must be in [0, 100]"};
        }
    }

    [[nodiscard]] bool accepts(int score) const
    {
        return score >= value_;
    }

private:
    int value_;
};
```

`ScoreLimit{60}.accepts(60)` returns `true`. The constructor validates the threshold, and `accepts` compares a score to it. The `explicit` keyword blocks implicit conversion from `int` to `ScoreLimit`. A `struct` can carry computed results, as in [`ScoreSummary`](../../../examples/cpp/score-summary.hpp).

<a id="templates"></a>

## Templates and constraints

Declare a template when the same operation applies to several types. Constrain the accepted types with a concept when the operation has specific requirements.

Function definition excerpt. Include `<concepts>`.

```cpp
template <std::integral T>
constexpr bool at_least(T value, T minimum)
{
    return value >= minimum;
}

static_assert(at_least(60, 60));
```

The compiler checks the condition in `static_assert`. This template deduces one `T` for both arguments. A call with `at_least(60, 60L)` requires the types to be reconciled explicitly. Usually put the template definition in a header so the compiler can see it at the point of use.

<a id="ranges"></a>

## Lambdas and ranges

Use an algorithm when you need an immediate result. Use a view to iterate over only the elements that match.

Function body excerpt. Include `<algorithm>`, `<ranges>`, and `<vector>`.

```cpp
std::vector<int> scores{55, 60, 95};
int minimum = 60;
const auto passes = [minimum](int score) { return score >= minimum; };

const auto count = std::ranges::count_if(scores, passes);
auto passing_scores = scores | std::views::filter(passes);
```

`count` equals 2. Iteration over `passing_scores` yields 60 and 95. The `[minimum]` capture copies the threshold when the lambda is created. A reference capture requires the object to stay available until the call. This filter view refers to the vector and evaluates matches during iteration. Keep the vector alive and follow its iterator invalidation rules.

<a id="standard-library"></a>

## Choose a standard library component

| Task | Header and API | Condition |
| --- | --- | --- |
| Store a sequence | `<vector>` `std::vector`, `<array>` `std::array` | A `vector` can resize. An `array` encodes its size in its type. |
| Look up values by key | `<map>` `std::map`, `<unordered_map>` `std::unordered_map` | A `map` keeps keys ordered. An `unordered_map` uses hashing. |
| Own or read text | `<string>` `std::string`, `<string_view>` `std::string_view` | A `string` owns its contents. A `string_view` refers to existing storage. |
| Sort or find elements | `<algorithm>` · `std::ranges::sort(scores)`, `std::ranges::find(scores, 60)` | For the vector `scores` above, sorting changes the order of the elements. If the value is missing, the search returns `scores.end()`. |
| Represent an optional value or one of several types | `<optional>` `std::optional`, `<variant>` `std::variant` | Check for a value or check the active type. |
| Work with paths, files, and time | `<filesystem>` `std::filesystem::path`, `<fstream>` `std::ifstream`, `<chrono>` `std::chrono::steady_clock` | Check I/O errors. Use a monotonic clock to measure elapsed time. |
| Run work in a thread and protect data | `<thread>` `std::jthread`, `<mutex>` `std::scoped_lock` | Define who owns the data and how every access is synchronized. |

<a id="errors"></a>

## Absence and errors

| Situation | Technique | Example |
| --- | --- | --- |
| A value may be absent during normal operation | `std::optional<T>`, `std::nullopt` | Search for the first qualifying score. |
| An argument violates the function contract | Typed exception | The lab throws `std::invalid_argument` for a score outside the accepted range. |
| Failure is part of the API protocol | Error code or result object | `std::from_chars` returns a position and a `std::errc`. |

Function excerpt. Include `<optional>` and `<span>`.

```cpp
std::optional<int> first_at_least(std::span<const int> scores, int minimum)
{
    for (int score : scores) {
        if (score >= minimum) {
            return score;
        }
    }
    return std::nullopt;
}
```

With 55, 60, 95 and a threshold of 60, the function returns 60. With empty input it returns `std::nullopt`. Check that a value exists before dereferencing. In the [CLI example](../../../examples/cpp/score-count.cpp), check both fields of the `from_chars` result. The function can accept the numeric prefix of a string. The CLI adapter converts argument errors into a message and exit status 2.

## Sources

- [WG21 N4861 C++20 draft](https://github.com/cplusplus/draft/tree/n4861/source) · [Feature support in Clang](https://clang.llvm.org/cxx_status#cxx20).
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines) · [Ownership and object lifetimes](practice.md#lifetimes).
