<a id="проверить-json-http-запрос"></a>
# Validate a JSON HTTP request

[Русский](../../ru/go/http-json.md)

Open this page to accept a name through JSON and distinguish malformed input, an empty name, and an oversized body.
The POST `/normalize` example runs in-process. Registration and database persistence are outside its scope.
[Go reference](README.md) · [Module](language.md#complete-module)

| Task | Technique | Example |
| --- | --- | --- |
| Accept a name and trim whitespace | Handler with type and semantic validation | [Successful request](#handler-with-input-boundaries) |
| Reject extra data or a large body | Size limit and a single JSON value check | [Input boundaries](#distinguish-input-errors) |
| Test a response without starting a server | `httptest.NewRecorder` | [Test](#test-without-a-network-server) |
| Handle external requests | Timeouts, resources, and shutdown | [Operational boundaries](#before-serving-real-http-traffic) |

**Level** — intermediate → advanced.
Prerequisites include HTTP, structs, and errors. Go 1.27 is required.
The example uses only `encoding/json`, `net/http`, and `httptest` from the standard library.
Save the [complete http.go and http_test.go](examples/http-json.md#handler-with-input-boundaries) with `go.mod` following the [example setup](examples/http-json.md#setup).

<a id="handler-с-границами-ввода"></a>
## Handler with input boundaries

A client sends `{"name":" Alice "}`. The response must contain the name `Alice`.
The handler must reject an unsuitable Content-Type and an empty name before writing a successful response.
Normalize the name after parsing JSON.

**Example snippet inside a test in the complete module, importing `net/http`, `net/http/httptest`, and `strings`**

```go
request := httptest.NewRequest(http.MethodPost, "/normalize", strings.NewReader(`{"name":" Alice "}`))
request.Header.Set("Content-Type", "application/json")
recorder := httptest.NewRecorder()
NewHandler().ServeHTTP(recorder, request)
// recorder.Code == 200
// recorder.Body.String() == "{\"name\":\"Alice\"}\n"
```

The handler returns `200`, `application/json`, and the normalized name.
The `1 KiB` body limit was chosen for this learning request. Define your own limit according to the contract.
The handler checks for response-write errors, but a status already sent cannot be changed.

[Complete http.go](examples/http-json.md#handler-with-input-boundaries)

<a id="различить-ошибки-ввода"></a>
## Distinguish input errors

An untrusted client can send malformed JSON, an extra field, or a second object.
Check the format, size, and number of values separately from the nonempty-name rule.

**Example decoder configuration snippet inside `normalizeName`**

```go
r.Body = http.MaxBytesReader(w, r.Body, maxBodyBytes)
decoder := json.NewDecoder(r.Body)
decoder.DisallowUnknownFields()
```

The snippet requires the complete handler with `maxBodyBytes`, error handling, and a second `Decode` call that expects `io.EOF`.
A single `Decode` call alone does not reject a second JSON value.

| POST `/normalize` input | Expected status | Reason |
| --- | --- | --- |
| `{"name":" "}` | `422` | Name is empty after trimming whitespace |
| `{"name":` | `400` | Malformed JSON |
| `{"name":123}` | `400` | Incorrect field type |
| `{"name":"Alice","extra":1}` | `400` | Unknown field |
| `{"name":"Alice"}{"name":"Bob"}` | `400` | More than one JSON value |
| Body larger than `1024` bytes | `413` when the excess is detected | Learning-example limit exceeded |
| Request without `application/json` | `415` | Incorrect content type |

The handler can reject another violation before detecting the size excess.
`DisallowUnknownFields` neither rejects duplicate keys nor makes field names case-sensitive.
If the contract restricts these cases, add a separate check.

[Complete error handling](examples/http-json.md#handler-with-input-boundaries)

<a id="тест-без-сетевого-сервера"></a>
## Test without a network server

Save the [complete http_test.go](examples/http-json.md#test-without-a-network-server).
Run `go test -count=1 ./...` from the module directory.
Expect name normalization and separate `400/405/413/415/422` rejections.
GET `/normalize` returns `405`.
The recorder calls the handler without opening a TCP port.

<a id="перед-настоящим-http-запуском"></a>
## Before serving real HTTP traffic

| Task | Configuration |
| --- | --- |
| Accept external requests | `http.Server` with `ReadHeaderTimeout`, `IdleTimeout`, and a body/deadline policy. Values depend on streaming and clients |
| Limit JSON | Body size and structure/item-count limits according to requirements. Size does not describe the full processing cost |
| Send outgoing requests | Reusable `http.Client` with a timeout, `NewRequestWithContext`, closing `response.Body`, and bounded reading |
| Stop the server | `Server.Shutdown` with a bounded context. Manage background tasks separately |
| Verify operation | Test TLS, proxies, load, connection closing, and request cancellation in separate scenarios |

<a id="источники"></a>
## Sources

[encoding/json](https://pkg.go.dev/encoding/json), [net/http](https://pkg.go.dev/net/http),
[httptest](https://pkg.go.dev/net/http/httptest), [context](https://pkg.go.dev/context),
[Go 1.27 release notes](https://go.dev/doc/go1.27).
