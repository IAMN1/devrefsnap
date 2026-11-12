# Ownership, patterns, and applications in C++

[C++ reference](README.md) · [Русский](../../ru/cpp/practice.md)

Use these cards when a program manages resources, passes data between components, or brings in an external library. The snippets use C++20.

| Task | Technique | Example |
| --- | --- | --- |
| Close a file or release memory | RAII and the Rule of Zero | [Resource ownership](#ownership) |
| Check a reference lifetime or transfer ownership | `std::span`, `std::unique_ptr`, `std::move` | [Lifetimes](#lifetimes) |
| Replace a scoring rule or connect a new interface | Strategy and Adapter | [Patterns](#patterns) |
| Choose a domain and a first project | Tools and constraints by domain | [Application areas](#application-areas) |

<a id="ownership"></a>

## Resource ownership

RAII (Resource Acquisition Is Initialization) ties resource acquisition to object initialization. The object's destructor releases the resource on scope exit, including during exception unwinding. Use a stream for a file. Use `std::scoped_lock` from `<mutex>` for a lock.

Function body excerpt. Include `<fstream>`, `<stdexcept>`, and `<string>`. The variable `path` identifies a text file containing at least one line, which may be blank.

```cpp
std::ifstream input{path};
std::string line;
if (!std::getline(input, line)) {
    throw std::runtime_error{"could not read the first line"};
}
```

On success, `line` holds the first line without its delimiter. Reading fails if the file is empty or inaccessible. The stream closes the file when `input` is destroyed.

Apply the Rule of Zero. When members already manage the resources, use the generated copy, move, and destruction operations.

Type definition excerpt. Include `<string>` and `<vector>`.

```cpp
struct ScoreBatch {
    std::string label;
    std::vector<int> scores;
};
```

A copy of `ScoreBatch` gets its own member values. Its members release their resources when the object is destroyed. To wrap a resource from a C API, first check whether `std::unique_ptr` with a custom deleter fits.

<a id="lifetimes"></a>

## Lifetimes and moves

| Intent | Tool | Condition |
| --- | --- | --- |
| Keep data in an object | Value members, `std::string`, `std::vector` | The object manages the lifetime of its data. |
| Transfer exclusive ownership | `std::unique_ptr<T>`, `std::move` | The new owner releases the resource. |
| Share ownership | `std::shared_ptr<T>` | Several independent owners need the resource. Use `std::weak_ptr<T>` to observe it without extending its lifetime. |
| Borrow data | `T&`, pointer, `std::span`, `std::string_view` | The owner must keep the storage available. |

Function body excerpt. Include `<memory>` and `<utility>`.

```cpp
auto owner = std::make_unique<int>(60);
auto new_owner = std::move(owner);
```

`*new_owner` equals 60, and `owner` is empty after the move. The `std::move` call allows a move operation to be selected. The `unique_ptr` constructor transfers ownership. For other types, check the guarantees about the moved-from state before reading the object.

A reference, pointer, or view can outlive the data it refers to. Return local data by value. If `push_back` reallocated vector storage, reacquire pointers, references, and iterators. If a view refers to that storage, recreate the view. [Vector rules in the standard draft](https://github.com/cplusplus/draft/blob/n4861/source/containers.tex) · [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines).

<a id="patterns"></a>

## Patterns and component boundaries

| Task | Pattern | C++ technique |
| --- | --- | --- |
| Replace a selection rule | Strategy | Pass a lambda or function object to an algorithm. |
| Convert external input for a function | Adapter | Translate arguments and errors at the CLI boundary. |
| Select an implementation from configuration | Factory | Return a `std::unique_ptr<Interface>` when the caller takes ownership. Give the interface a virtual destructor. |
| Notify several components of an event | Observer | Register callbacks. Tie unsubscription to the lifetime of the subscription object. |
| Manage the lifetime of a resource | RAII | Store the resource in an object with the appropriate release operation. |

Function body excerpt. Include `<algorithm>` and `<array>`. The algorithm stays the same when the predicate changes.

```cpp
const std::array scores{55, 60, 100};
const auto passing = std::ranges::count_if(scores, [minimum = 60](int score) {
    return score >= minimum;
});
const auto perfect = std::ranges::count_if(scores, [](int score) {
    return score == 100;
});
```

`passing` equals 2 and `perfect` equals 1. Each lambda supplies a separate counting rule. If a caller must store different strategy types in one variable, consider `std::function` with a common signature.

The lab's CLI adapter converts strings into `int` values and passes the data to the scoring function through a `std::span`. The adapter converts `std::invalid_argument` into a message and exit status 2. Switching input methods preserves the scoring contract if the adapter supplies the same arguments. [CLI adapter](../../../examples/cpp/score-count.cpp) · [Scoring contract](../../../examples/cpp/score-summary.hpp) · [Running tests](tooling-and-testing.md#tests).

Validate data when it enters a component. Start diagnosis by enabling compiler warnings and running tests. If performance matters, measure time and resource use with data that resembles the real workload. [Lab diagnostics](tooling-and-testing.md#diagnostics) · [Google Benchmark](https://github.com/google/benchmark).

<a id="application-areas"></a>

## Where C++ is used

Choose one domain and one task. Check the selected library's documentation for support on your target platform.

| Domain | Tools and libraries | Skill | First task | Constraint |
| --- | --- | --- | --- | --- |
| Command-line and system utilities | [CMake and CTest](tooling-and-testing.md), `<filesystem>`, `<fstream>` | Input parsing, paths, exit codes | Count files with a particular extension | Account for OS permissions and path rules. |
| Desktop UI | [Qt 6 Widgets](https://doc.qt.io/qt-6/qtwidgets-index.html), CMake | Event loop, signals and slots | Display scoring results in a window | A long calculation can block the UI thread. |
| Games and interactive graphics | [SDL3](https://wiki.libsdl.org/SDL3/FrontPage), [Unreal Engine C++](https://dev.epicgames.com/documentation/en-us/unreal-engine/programming-with-cplusplus-in-unreal-engine) | Input, frame loop, resource loading | Move an object with the keyboard | For Unreal Engine, check the [development toolchain requirements](https://dev.epicgames.com/documentation/en-us/unreal-engine/setting-up-your-development-environment-for-cplusplus-in-unreal-engine) for the engine version and platform. |
| Embedded systems | [Zephyr](https://docs.zephyrproject.org/latest/develop/languages/cpp/index.html), Zephyr SDK | Cross-compilation, GPIO, memory | Blink an LED on a supported board | Check standard library and exception support for the configuration. |
| Network services | [Boost.Asio](https://www.boost.org/library/latest/asio/), [gRPC C++](https://grpc.io/docs/languages/cpp/) | Asynchronous operations, cancellation, timeouts | Expose scoring over a local RPC | Set deadlines and define shutdown order. |
| Low-latency systems | [Linux `perf`](https://docs.kernel.org/process/debugging/userspace_debugging_guide.html), `std::chrono::steady_clock` | Profiling, queueing delays | Replay recorded or synthetic messages and measure [p95 and p99 latency](https://sre.google/sre-book/service-level-objectives/) | Compare runs using the same hardware, build settings, and workload. |
| Numerical computing | [Eigen](https://libeigen.gitlab.io/), [Google Benchmark](https://github.com/google/benchmark) | Linear algebra, precision, profiling | Multiply two matrices and check the result | Record input size, precision, and build settings. |
| Python extensions | [pybind11](https://pybind11.readthedocs.io/en/stable/), CMake | Type conversion, ownership, packaging | Call the scoring function from Python | Check compatibility with Python and the target platform. |
