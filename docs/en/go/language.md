<a id="язык-модуль-и-ошибки"></a>
# Language, modules, and errors

[Русский](../../ru/go/language.md)

Open this page to review input handling, object mutation, and collection operations.
The examples use a user with a name and age. Invalid input must not create or change the object.
[Go reference](README.md) · [Concurrency](concurrency-and-testing.md) · [HTTP](http-json.md)

| Task | Technique | Example |
| --- | --- | --- |
| Create a user from strings | Validate input and return an `error` | [Input and error causes](#validate-input-and-inspect-an-errors-cause) |
| Rename an existing user | Pointer receiver and validation before writing | [Object mutation](#mutate-an-object-and-preserve-its-interface) |
| Change a copy of a list independently | Copy slice elements | [Collections and generics](#copy-a-slice-and-check-an-element) |
| Review syntax | Short constructs | [Language table](#basic-constructs) |
| Build the program and tests | One module without external libraries | [Complete module](#complete-module) |

**Level** — beginner → intermediate.
Prerequisites include functions and collections. Running the examples requires Go 1.27.
The snippets below assume `import "example.com/cheatsheet"` in the complete module's `main` package.
Also import the listed standard packages.
The [complete files and tests](examples/language.md#complete-module) contain all imports.

<a id="проверить-ввод-и-причину-ошибки"></a>
## Validate input and inspect an error's cause

A form supplies the name `" Alice "` and the age as the string `"30"`.
Trim whitespace and distinguish an invalid age from an empty name.
Return an error before creating the user. Preserve its cause with `%w`.

**Example snippet inside `main`, with additional imports `errors` and `fmt`**

```go
user, err := cheatsheet.NewUser(" Alice ", "30")
if err != nil {
    fmt.Println(err)
    return
}
fmt.Println(user.Name, user.Age) // Alice 30
_, err = cheatsheet.NewUser("Alice", "-1")
fmt.Println(errors.Is(err, cheatsheet.ErrInvalidAge)) // true
```

Valid input creates a user. A negative age returns a recognizable cause.
`errors.Is` checks a cause in the chain. `errors.As` extracts an error of a particular type.
For example, `"not-a-number"` produces a `*strconv.NumError`.
`%v` formats text without preserving the chain.
Parsing an `int` depends on the architecture. For a fixed range, choose `int64` and the corresponding parser.

[NewUser implementation](examples/language.md#complete-module) · [Invalid-input tests](#test-valid-and-invalid-input)

<a id="изменить-объект-и-сохранить-интерфейс"></a>
## Mutate an object and preserve its interface

The user already exists. Renaming must change the original object only when the name is nonempty.
Validate the name before writing and use a pointer receiver for `Rename`.
Keep a value receiver on `String` if the method does not need to change the object.

**Example continuing the previous snippet, using `fmt` and `errors`**

```go
err = user.Rename("Alice Doe")
fmt.Println(err == nil, cheatsheet.Describe(user)) // true Alice Doe (30)
err = user.Rename(" ")
fmt.Println(errors.Is(err, cheatsheet.ErrEmptyName)) // true
fmt.Println(user.Name) // Alice Doe
```

An empty name leaves the user unchanged.
`User` satisfies `fmt.Stringer` without an `implements` declaration.
`Rename` assumes a non-nil pointer.
`log.Fatal` terminates the process with `os.Exit(1)` without running deferred functions.
In a library, return the error to the caller.

[Complete methods, interface, and main](examples/language.md#complete-module)

<a id="скопировать-срез-и-проверить-элемент"></a>
## Copy a slice and check an element

You need to change a list of numbers for a calculation while preserving the original list.
Copy the elements before changing them. Ordinary slice assignment shares the underlying array's memory.

**Independent example snippet inside `main`, with the additional import `fmt`**

```go
original := []int{1, 2, 3}
copied := cheatsheet.Clone(original)
copied[0] = 99
fmt.Println(original[0], copied[0]) // 1 99
fmt.Println(cheatsheet.Contains(original, 2)) // true
counts := cheatsheet.Counts([]string{"go", "go", "python"})
fmt.Println(counts["go"]) // 2
_, ok := counts["missing"]
fmt.Println(ok) // false
```

Changing a number in the copy leaves the original unchanged.
`Clone` copies elements. Nested pointers, maps, and slices can retain shared data.
`append` can allocate a new array. Save the returned slice.
`Contains[T comparable]` uses `==`. `any` does not permit arbitrary operations on the type.
`Counts` creates a map before writing. Map iteration order is unspecified.

[Collection implementation and tests](examples/language.md#test-valid-and-invalid-input)

<a id="основные-конструкции"></a>
## Basic constructs

| Task | Construct and limitation |
| --- | --- |
| Zero value | `0`, `false`, `""`. Slices/maps/pointers/channels/interfaces can be nil |
| Array / slice | `[3]int{1, 2, 3}` / `[]int{1, 2, 3}`. Array length is part of its type |
| Create a map | `make(map[string]int)`. Reading a missing key returns the zero value |
| Check a key | `value, ok := counts["python"]`. `ok` distinguishes a missing key from zero |
| Pointer | `p := &user`, `*p`. Ordinary Go has no pointer arithmetic |
| Loop | `for i := 0; i < n; i++`, `for condition`, `for key, value := range data` |
| Condition with initialization | `if value, ok := m[key]; ok { ... }` is a syntax fragment |
| Function as a value | `func(string) string`. A closure can capture mutable data |
| Constants | `const`, with `iota` for sequences when needed |
| Discard a value | `_`. Avoid using `_` to silently ignore an important error |

The table contains syntax fragments and does not form a standalone program.

A string is an immutable sequence of arbitrary bytes. Valid UTF-8 is not guaranteed.
`len(s)` counts bytes.
`range` decodes UTF-8 and returns byte positions and runes.
For an invalid sequence, `range` returns `utf8.RuneError`.

`panic/recover` does not replace ordinary `error` returns.
`recover` works in a deferred function of the corresponding goroutine.
Since Go 1.22, `range` variables declared with `:=` are created separately on each iteration.
This behavior does not eliminate races on shared objects.

<a id="полный-модуль"></a>
## Complete module

[Open go.mod, model.go, and cmd/demo/main.go](examples/language.md#complete-module).
Save the files in a separate directory. Use the paths after `go/` in the example comments.
Run `go run ./cmd/demo`.
Expect `Alice Doe (30)` and `true`.

<a id="проверка-валидного-и-невалидного-ввода"></a>
## Test valid and invalid input

[Save the complete model_test.go](examples/language.md#test-valid-and-invalid-input).
Run `go test ./...` and `go vet ./...` from the module directory.

The tests confirm user creation and renaming, invalid-input rejection, and independent numeric elements in a slice copy.
A rejected rename preserves the previous name.

<a id="источники"></a>
## Sources

[Specification](https://go.dev/ref/spec), [Go 1.27 release notes](https://go.dev/doc/go1.27),
[loop variable changes in Go 1.22](https://go.dev/doc/go1.22#language),
[creating a module](https://go.dev/doc/tutorial/create-module), [generics](https://go.dev/doc/tutorial/generics),
[errors](https://pkg.go.dev/errors), [strconv](https://pkg.go.dev/strconv).
