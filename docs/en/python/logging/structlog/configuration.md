<a id="настроить-вывод-и-процессоры"></a>
# Configure output and processors

[Русский](../../../../ru/python/logging/structlog/configuration.md)

Use this page to produce JSON events, preserve tracebacks, or integrate structlog with standard library logging.
Configure logging once before processing events.

| Task | Technique | Example or details |
| --- | --- | --- |
| Choose JSON, console, or key-value output | One final renderer | [Standalone configuration](#standalone-configuration) |
| Mask known fields | Processor before the renderer | [Code and checks](#standalone-configuration) |
| Combine two logging sources | `ProcessorFormatter` | [Standard library logging](#integrate-with-standard-library-logging) |
| Avoid computing an expensive DEBUG argument | Check the level before calling | [Ordering and cost](#ordering-and-cost) |

[Reference](README.md) · [Context and web](context-and-web.md)

The level ranges from basic to advanced.
Prerequisites include dictionaries, logging, and exception handling.
Use Python 3.14.
Run `python -m pip install 'structlog==26.1.0' 'pytest==9.2.0'` in a separate environment.
Keep all files for this topic in one directory.

- [Standalone configuration](#standalone-configuration)
- [Standard library logging integration](#integrate-with-standard-library-logging)
- [Ordering and cost](#ordering-and-cost)

<a id="самостоятельная-конфигурация"></a>
## Standalone configuration

The complete `demo_logging.py` chooses a renderer once.
It recursively masks sensitive fields by a specified set of names.

[`structlog/demo_logging.py`](../../../../../examples/python/logging/structlog/demo_logging.py)

Run `python demo_logging.py`.
The output contains two JSON lines.
The password is replaced with `***`.
The second line has an `exception` field with a traceback.
Masking applies only to the listed **keys**.
Strings, tracebacks, and unsupported containers remain untouched.
Keep secrets out of `event` and exception text.

Masking preserves tuples.
An `exc_info` value saved with `sys.exc_info()` must remain a tuple.
ConsoleRenderer can then reconstruct the traceback outside `except`.

Complete `test_logging.py` follows.

[`structlog/test_logging.py`](../../../../../examples/python/logging/structlog/test_logging.py)

<a id="интеграция-со-stdlib-logging"></a>
## Integrate with standard library logging

The complete `demo_stdlib.py` configures only a practice logger name.
Integrate this configuration into the application's normal setup.
Keep other handlers intact when importing a library.

[`structlog/demo_stdlib.py`](../../../../../examples/python/logging/structlog/demo_stdlib.py)

The complete `test_stdlib.py` checks both sources through one chain.

[`structlog/test_stdlib.py`](../../../../../examples/python/logging/structlog/test_stdlib.py)

Run `python -m pytest -q test_logging.py test_stdlib.py`.
Here the final renderer belongs to `ProcessorFormatter`.
The structlog chain ends with `wrap_for_formatter`.
`foreign_pre_chain` enriches ordinary logging records.
`remove_processors_meta` removes internal fields before JSON rendering.
`get_logger` and `wrap_logger` return structlog bound loggers even when wrapping a `logging.Logger`.

<a id="порядок-и-стоимость"></a>
## Ordering and cost

| Processor or technique | When to use it |
| --- | --- |
| `merge_contextvars` | First, when request context is required |
| `filter_by_level` | Early filter for a stdlib logger. Python has already evaluated call arguments. |
| `TimeStamper`, `add_log_level`, `add_logger_name` | Metadata. Logger names require suitable stdlib context. |
| `PositionalArgumentsFormatter` | `%s` arguments in stdlib-style calls |
| `StackInfoRenderer` | `stack_info=True`, which captures a different stack from `exc_info` |
| `format_exc_info` | Exception formatting for text or JSON. ConsoleRenderer has its own exception formatting. |
| `UnicodeDecoder` | When the event dictionary actually contains bytes |
| `CallsiteParameterAdder` | FILENAME, FUNC_NAME, and LINENO when the additional cost is justified |
| `JSONRenderer`, `KeyValueRenderer`, or a custom renderer | Final step. Return a format accepted by the underlying logger. |

A custom renderer has the signature `(logger, method_name, event_dict)`.
Preserve all required fields.
Building a string from only event and level discards other data.
To use another JSON encoder, supply a compatible `serializer`.
For example, install orjson and pass `orjson.dumps`.
Use a serializer that produces valid JSON from the entire event dictionary.

Python evaluates arguments **before** logger filtering.
Thus `log.debug("event", value=expensive())` calls expensive even if DEBUG is disabled.
With the filtering logger shown here, check `log.is_enabled_for(logging.DEBUG)` first.
The stdlib BoundLogger offers `isEnabledFor`.
Check the wrapper class API before using either method.
Set `cache_logger_on_first_use` once.
Repeating a keyword argument in one call is a syntax error.
After reconfiguration, obtain a fresh logger in tests.

See [configuration](https://www.structlog.org/en/stable/configuration.html), [processors and API](https://www.structlog.org/en/stable/api.html), [stdlib integration](https://www.structlog.org/en/stable/standard-library.html), [exceptions](https://www.structlog.org/en/stable/exceptions.html), and [performance](https://www.structlog.org/en/stable/performance.html).
