<a id="полный-модуль-язык-и-ошибки"></a>
# Complete module for language and errors

[Русский](../../../ru/go/examples/language.md)

Open this page to assemble the complete code after the [short cards](../language.md).

| Task | Technique | Example |
| --- | --- | --- |
| Create and run a module | `go.mod + model + main` | [Complete module](#complete-module) |
| Validate input and preserve the object | `NewUser and Rename tests` | [Tests](#test-valid-and-invalid-input) |

[Go reference](../README.md) · [Concurrency](../concurrency-and-testing.md) · [HTTP](../http-json.md)

<a id="подготовка"></a>
## Setup

Prerequisites include functions and collections.
Running the example requires Go 1.27.
Create a separate learning directory.
Save the files from this page there.
All blocks with filenames form one module without third-party dependencies.
Preserve relative paths after `go/`.

See the [quick reference](../language.md#basic-constructs) for basic constructs and `range` limitations.

<a id="полный-модуль"></a>
## Complete module

<a id="go-mod"></a>

The `go.mod` file follows.

[`go/go.mod`](../../../../examples/go/go.mod)

Complete `model.go` follows.

[`go/model.go`](../../../../examples/go/model.go)

The `String` method's value receiver lets `User` satisfy `fmt.Stringer`.
The `Rename` method's pointer receiver mutates the original object.
`Rename` assumes a non-nil pointer.
`Clone` copies slice elements.
`Clone` does not deep-copy objects referenced by the elements.
The `comparable` constraint permits `==` comparisons.
The `any` constraint does not permit arbitrary operations on T.

Complete `cmd/demo/main.go` follows.

[`go/cmd/demo/main.go`](../../../../examples/go/cmd/demo/main.go)

`go run ./cmd/demo` prints `Alice Doe (30)` and `true`.
`log.Fatal` calls `os.Exit(1)`.
Deferred functions do not run when the process exits this way.
In a library function, return the error to the caller.

<a id="проверка-валидного-и-невалидного-ввода"></a>
## Test valid and invalid input

Complete `model_test.go` follows. The tests belong to the package and require no external service.

[`go/model_test.go`](../../../../examples/go/model_test.go)

Run `go test ./...`.
Then run `go vet ./...`.
`fmt.Errorf("...: %w", err)` preserves the cause chain.
`%v` only formats text.
If you need an error type or cause, avoid treating text comparison as a stable contract.
Number parsing checks the format and the current architecture's int range.
For serializable identifiers, choose an explicit `int64` and its corresponding parser when required.

Sources include the [specification](https://go.dev/ref/spec), [creating a module](https://go.dev/doc/tutorial/create-module), [generics](https://go.dev/doc/tutorial/generics), [errors](https://pkg.go.dev/errors), and [strconv](https://pkg.go.dev/strconv).
