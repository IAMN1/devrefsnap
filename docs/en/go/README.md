
# Go

[Русский](../../ru/go/README.md)

[Find an example by task or synonym](../tasks/README.md#go-language-and-concurrency) · [HTTP and JSON](../tasks/README.md#http-apis-and-web-applications).

Go is a statically typed, compiled language. It supports small interfaces, explicit errors, and concurrency primitives.
Open this section to review syntax, error handling, concurrency, or HTTP input validation.
The section contains a quick reference and independent learning examples with no third-party dependencies.

[Main catalog](../README.md)

<a id="быстрый-поиск"></a>
## Quick lookup

| Task | Technique | Details |
| --- | --- | --- |
| Create a module and run a program | `go.mod`, `go run ./cmd/demo` | [Complete example setup](examples/language.md#setup) |
| Variables, loops, slices/maps/pointers | Standard syntax | [Syntax](language.md#basic-constructs) |
| Struct, method, interface, generics | Value/pointer receivers, type constraints | [Object and interface](language.md#mutate-an-object-and-preserve-its-interface) |
| Error with a cause | `%w`, `errors.Is`, `errors.As` | [Reference card](language.md#validate-input-and-inspect-an-errors-cause) · [Input tests](examples/language.md#test-valid-and-invalid-input) |
| Cancellation, channels, and bounded workers | `context`, `select`, `WaitGroup` | [Concurrency](concurrency-and-testing.md) |
| Cancel an outgoing HTTP request or set a deadline | `context.WithCancel`, `context.WithTimeout` | [HTTP request context](context.md) |
| Protect shared state | `sync.Mutex` | [Counter](concurrency-and-testing.md#shared-data-and-mutexes) |
| JSON/HTTP, limits, tests | `json.Decoder`, `MaxBytesReader`, `httptest` | [HTTP and JSON](http-json.md) |
| Formatting, tests, analysis, races | `gofmt`, `go test`, `go vet`, `-race` | [Commands](#module-commands) |

| Parameter | Value |
| --- | --- |
| Language release | Go 1.27. `go.mod` sets the minimum language version for the example |
| Prerequisites | Variables, functions, data structures. Concurrency requires understanding shared data |

<a id="навигация"></a>
## Navigation

- [Quick lookup](#quick-lookup)
- [Module commands](#module-commands)
- [Before the first recipe](#before-the-first-recipe)
- [Collections and interfaces](#collections-and-interfaces)
- [Concurrency and HTTP](#concurrency-and-http)
- [Common mistakes](#common-mistakes)
- [Sources](#sources)

<a id="базовый-уровень"></a>

<a id="команды-модуля"></a>
## Module commands

Choose a complete example for the [language](examples/language.md), [concurrency](examples/concurrency-and-testing.md), or [HTTP](examples/http-json.md).
Save the selected example's files in a separate learning directory.
The installed Go version must support the version in `go.mod`.
The commands below require no third-party libraries.
`go run ./cmd/demo` applies to the language example. The other commands apply to every example.

```bash
go version
gofmt -w .
go run ./cmd/demo
go test ./...
go vet ./...
go test -race ./...
```

`gofmt -w` rewrites formatting in the learning directory's `.go` files.
`go run` compiles and runs the program.
`go test` runs tests.
`vet` checks suspicious constructs.
The race detector finds races only on executed paths.
The race detector requires a supported platform and build tools.
A successful check does not prove the absence of all races.

If a new project has no `go.mod`, run `go mod init example.com/cheatsheet`.
`go mod tidy` synchronizes dependencies with imports.
The command can change `go.mod`/`go.sum`.
When external modules are present, the command can access the network.
This example has no external modules.
To disable automatic toolchain downloads, set `GOTOOLCHAIN=local` in the environment.
If the installed Go version is older than the version in `go.mod`, the command fails. Update Go explicitly.

<a id="что-знать-до-первого-рецепта"></a>
## Before the first recipe

| Construct | Meaning |
| --- | --- |
| `package`, `import` | One package per directory. Import the dependencies you use |
| `var n int`, `name := "Alice"` | Declaration. Use `:=` inside a function |
| `func f(x int) (int, error)` | Argument types and multiple results |
| `if`, `switch`, `for`, `range` | Conditions, selection, loops. There is no separate `while` |
| `defer f()` | Run when the function exits. Arguments are evaluated at the defer statement |
| Capitalized name | Exported from the package |

<a id="средний-уровень"></a>

<a id="коллекции-и-интерфейсы"></a>
## Collections and interfaces

The [language recipe](language.md) shows a pointer receiver, a consumer-defined interface, slice copying, and generic functions.
Errors are checked with `errors.Is`/`As`.
Strings, maps, and other constructs appear in the [language table](language.md#basic-constructs).

<a id="продвинутый-уровень"></a>

<a id="конкурентность-и-http"></a>
## Concurrency and HTTP

The [worker pool](concurrency-and-testing.md) limits the number of goroutines and waits for them to finish.
Context cancellation is cooperative. Choose a channel or mutex based on data ownership.
The [cancellation and deadline example](context.md) sends requests to a local HTTP server.
The [HTTP recipe](http-json.md) separates JSON syntax from data semantics.
The recipe tests the handler with `httptest.NewRecorder`. External server settings are covered [separately](http-json.md#before-serving-real-http-traffic).

<a id="частые-ошибки"></a>
## Common mistakes

| Mistake | Correction |
| --- | --- |
| Comparing errors by their text | Use `errors.Is` for a cause and `errors.As` for a type |
| `interface != nil` although it contains a nil pointer | An interface is nil only when it has neither a dynamic type nor a value |
| Several goroutines write to a map | Protect the map with a mutex or assign a single owner |
| Treating a read from a closed channel as a regular read | Check `value, ok`. Closing a channel is not a job value |
| The receiver closes the channel | The side that knows all senders have finished closes it |
| Using `time.Sleep` for synchronization | Use a channel, WaitGroup, or context. Bound test duration |
| Losing the result of append | Assign the returned slice |

<a id="источники"></a>
## Sources

- [Go 1.27 release notes](https://go.dev/doc/go1.27), [release history](https://go.dev/doc/devel/release), [specification](https://go.dev/ref/spec).
- [Go command](https://pkg.go.dev/cmd/go), [gofmt](https://pkg.go.dev/cmd/gofmt), [modules](https://go.dev/doc/modules/gomod-ref).
- [Effective Go](https://go.dev/doc/effective_go) helps with style. The document itself warns that it does not cover modern generics/modules. It is not a complete, up-to-date tutorial.
