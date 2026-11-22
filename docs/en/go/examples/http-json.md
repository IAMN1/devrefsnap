<a id="полный-пример-json-handler-и-тесты"></a>
# Complete example with a JSON handler and tests

[Русский](../../../ru/go/examples/http-json.md)

The example accepts a name through JSON and tests successful responses and input errors without a TCP server.
The [short cards](../http-json.md) explain individual techniques.

| Task | Technique | Example |
| --- | --- | --- |
| Accept bounded JSON input | `POST /normalize handler` | [Handler](#handler-with-input-boundaries) |
| Test success and errors | `httptest without a TCP server` | [Tests](#test-without-a-network-server) |

[Go reference](../README.md) · [Module](language.md#complete-module)

<a id="подготовка"></a>
## Setup

Running the example requires Go 1.27.
Prerequisites include HTTP, structs, and errors.
From the repository root, run `go -C examples/go test -run 'TestJSONHandler|TestMethodAndMediaType' .`. The tests report `ok` followed by the module name on success.

To assemble the example separately, copy [go.mod](../../../../examples/go/go.mod) into a learning directory.
Save `http.go` and `http_test.go` from the links below beside `go.mod`.
The example uses only the standard library, including `encoding/json`, `net/http`, and `httptest`.

<a id="handler-с-границами-ввода"></a>
## Handler with input boundaries

Complete `http.go` contains the POST `/normalize` handler.
The handler accepts a name, trims whitespace, and returns JSON.
The example handles input without registration or database persistence.
The 1 KiB limit was chosen solely for the learning request body.

[`go/http.go`](../../../../examples/go/http.go)

The handler checks JSON syntax, the number of JSON values, and the name's business rule separately.
`DisallowUnknownFields` rejects unknown fields.
`DisallowUnknownFields` does not reject duplicate keys or eliminate all `encoding/json` case-matching behavior.
If the contract restricts these cases, add a separate check.
The handler checks response-write errors after sending begins.
A status already sent cannot be changed.

<a id="тест-без-сетевого-сервера"></a>
## Test without a network server

Complete `http_test.go` follows.

[`go/http_test.go`](../../../../examples/go/http_test.go)

Run `go test ./...`.
Expect name normalization and separate 400/405/413/415/422 rejections.
The recorder tests the handler in-process without opening a port.

<a id="перед-настоящим-http-запуском"></a>
## Before serving real HTTP traffic

The example tests the handler in-process.
For external requests, choose [timeouts, limits, resource closing, and server shutdown](../http-json.md#before-serving-real-http-traffic).
TLS, proxies, load, and request cancellation require testing in the target environment.

Sources include [encoding/json](https://pkg.go.dev/encoding/json), [net/http](https://pkg.go.dev/net/http), [httptest](https://pkg.go.dev/net/http/httptest), and [context](https://pkg.go.dev/context).
