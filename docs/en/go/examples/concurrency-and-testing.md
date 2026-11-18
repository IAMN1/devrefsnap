<a id="полный-пример-workers-и-счётчик"></a>
# Complete example with workers and a counter

[Русский](../../../ru/go/examples/concurrency-and-testing.md)

The example processes strings with several workers and protects a shared counter.
The [short cards](../concurrency-and-testing.md) explain individual techniques.

| Task | Technique | Example |
| --- | --- | --- |
| Process a list with cancellation | `Job channel + WaitGroup` | [Worker pool](#bounded-worker-pool) |
| Protect a shared counter | `Mutex for reading and writing` | [Counter](#shared-data-and-mutexes) |
| Check results and races | `Tests + race detector` | [Verification](#tests-and-the-race-detector) |

[Go reference](../README.md) · [Module files](language.md#complete-module)

<a id="подготовка"></a>
## Setup

Running the example requires Go 1.27.
Prerequisites include functions, slices, errors, and memory ownership.
Create a separate learning directory.
Copy [go.mod](language.md#go-mod) into the new directory.
Save `worker.go`, `counter.go`, and `worker_test.go` from the links below beside `go.mod`.
The example uses only the standard library, including `context` and `sync`.

<a id="ограниченный-worker-pool"></a>
## Bounded worker pool

The task is to process a string list with a bounded number of workers and preserve result order.
The producer closes the channel.
The caller receives the result only after all workers finish.

[See how the sender closes `jobs`, waits, and returns](../concurrency-and-testing.md#bounded-worker-pool).

Complete `worker.go` follows.

[`go/worker.go`](../../../../examples/go/worker.go)

The function preallocates the slice.
One worker writes each index.
Reading the result starts after Wait.
Keep the input slice unchanged during processing.
Workers check cancellation between jobs.
Cancellation does not interrupt `strings.ToUpper` halfway through an operation.
When several select cases are ready, cancellation has no absolute priority.
The example does not guarantee that no jobs run after cancel.

<a id="общие-данные-и-mutex"></a>
## Shared data and mutexes

Complete `counter.go` follows. When several goroutines change one counter, separate channel variables alone do not protect its value.

[`go/counter.go`](../../../../examples/go/counter.go)

The zero value of Counter is ready to use.
Pass Counter by pointer.
Do not copy a mutex after its first use.
Lock protects reads and writes of one invariant.
An atomic type can serve an independent counter.
Avoid mixing atomic and ordinary access to the same value.

<a id="тесты-и-race-detector"></a>
## Tests and the race detector

Complete `worker_test.go` follows.

[`go/worker_test.go`](../../../../examples/go/worker_test.go)

```bash
go test ./...
go vet ./...
go test -race ./...
```

Expect the original string order and the exact increment count.
Expect rejection for workers=0 or an already-canceled context.
The test timeout bounds processing.
The timeout does not prove the absence of all goroutine leaks.
`-race` detects races only on paths actually executed.
Logical race conditions and deadlocks require separate tests or analysis.
For repeatable diagnostics, use `go test -count=1 ./...`.
Avoid drawing conclusions solely from a cached run.

The function returns only the context error. Individual job errors are not modeled here.
The [synchronization and cancellation table](../concurrency-and-testing.md#tests-and-the-race-detector) covers rules for other scenarios.

Sources include [context](https://pkg.go.dev/context), [sync and synchronization semantics](https://pkg.go.dev/sync), the [memory model](https://go.dev/ref/mem), the [race detector](https://go.dev/doc/articles/race_detector), and [testing](https://pkg.go.dev/testing).
