# First steps with `asyncio`

[Русский](../../../ru/python/language/asyncio.md)

Use `asyncio` when several operations can wait for I/O at the same time.
Run a coroutine and compare two ways to wait for independent operations.

| Task | Technique | Example |
| --- | --- | --- |
| Run an async function | `async def`, `await`, `asyncio.run()` | [First coroutine](#run-a-coroutine) |
| Get results one at a time | Two calls with `await` | [Sequential waits](#wait-for-operations-sequentially) |
| Overlap waits | `asyncio.TaskGroup` | [Concurrent waits](#wait-for-operations-concurrently) |

Use Python 3.11 or newer for `TaskGroup`. The examples use only the standard library.
You need to know how to define and call a function.

## Run a coroutine

Calling an `async def` function creates a coroutine object without executing its body. To run the coroutine, await it or schedule it as a task.
In a regular script, run the top-level coroutine with `asyncio.run()`.

Save the complete example as `hello_async.py`.

```python
import asyncio


async def answer() -> int:
    print("running")
    return 42


async def main() -> None:
    coroutine = answer()
    print("created")
    print(await coroutine)


if __name__ == "__main__":
    asyncio.run(main())
```

Run `python3 hello_async.py` from the file's directory.
The script prints `created`, then `running`, then `42`.
`asyncio.run()` creates an event loop and closes it at the end. If an event loop is already running in the same thread, use `await` in async code.

## Wait for operations sequentially

Both independent operations in the example use the same `fetch()` function. The function waits for 0.2 seconds with `await asyncio.sleep(0.2)` and returns the name it received.
This simulates waiting for I/O without using the network.

In this fragment, `main()` awaits each coroutine separately.

```python
first = await fetch("A")
second = await fetch("B")
```

`fetch("B")` starts after `fetch("A")` finishes. The script gets `A` and `B` in about 0.4 seconds.

## Wait for operations concurrently

Add both coroutines to the same task group. While one task is waiting, the event loop can run another task that is ready.

This fragment of `main()` uses the `asyncio` import and the same `fetch()` function.

```python
async with asyncio.TaskGroup() as group:
    first_task = group.create_task(fetch("A"))
    second_task = group.create_task(fetch("B"))

print(first_task.result(), second_task.result())
```

When `async with` exits successfully, both tasks are finished. The script gets the same values in about 0.2 seconds because the waits overlap.
If a task raises an ordinary exception, the group requests cancellation of the remaining tasks and waits for them to finish.
Use sequential waits if the second operation needs the result of the first.

## Run the comparison

Open the [complete `demo.py` file](../../../../examples/python/language/asyncio/demo.py). Run the command from the repository root.

```bash
python3 examples/python/language/asyncio/demo.py
```

Example output. Elapsed time depends on scheduling and system load.

```text
sequential: A, B (0.40 s)
concurrent: A, B (0.20 s)
```

## Keep the event loop responsive

`time.sleep()` and synchronous HTTP clients block the event loop's thread when called directly. Long computations in that thread also delay other tasks.
Use `asyncio.sleep()` or an asynchronous I/O API for asynchronous waits. If only a blocking I/O function is available, `await asyncio.to_thread(...)` can run it in another thread.

Next, try [async tests with pytest](../testing/pytest/mocking-and-async.md#async-fixtures-and-the-event-loop) and [async sessions with SQLAlchemy](../databases/sqlalchemy/async-and-operations.md#async-session).

## Sources

- [Python 3.14 — running an asyncio program](https://docs.python.org/3.14/library/asyncio-runner.html#asyncio.run).
- [Python 3.14 — coroutines, tasks, and `TaskGroup`](https://docs.python.org/3.14/library/asyncio-task.html).
- [Python 3.14 — blocking code in `asyncio`](https://docs.python.org/3.14/library/asyncio-dev.html#running-blocking-code).
- [What's New in Python 3.11 — introduction of `TaskGroup`](https://docs.python.org/3.11/whatsnew/3.11.html#asyncio).
