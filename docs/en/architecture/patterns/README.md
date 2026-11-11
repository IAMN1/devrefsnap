<a id="паттерны-выбрать-приём-по-задаче"></a>
# Choose a pattern by task

[Русский](../../../ru/architecture/patterns/README.md)

A pattern provides a known solution structure with conditions and costs.
Choose a technique by task.
Inspect the roles and call.
Then open the complete example.

<a id="быстрый-поиск"></a>
## Quick lookup

| Task | Consider | Short card / example |
| --- | --- | --- |
| Replace a calculation algorithm | Strategy | [Roles and two rates](design-patterns.md#strategy-for-algorithm-substitution) |
| Translate units / an API | Adapter | [Grams and kilograms](design-patterns.md#adapter-for-translating-an-external-contract) |
| Add an action around a call | Decorator | [Audit wrapper](design-patterns.md#decorator-for-behavior-around-a-call) |
| Select and assemble an implementation | Factory | [Rate selection](design-patterns.md#factory-for-assembling-the-required-implementation) |
| Notify listeners in-process | Observer | [Subscriptions and errors](design-patterns.md#observer-for-notifying-local-subscribers) |
| Pass a request separately from execution | Command | [Request and handler](design-patterns.md#command-for-passing-an-action-as-data) |
| Find a source-code layout | Layered / Vertical Slice / Ports & Adapters | [Three trees and diagrams](architecture-patterns.md#code-organization) |
| Choose release boundaries | Modular Monolith / Microservices | [Deployment](architecture-patterns.md#deployment-boundaries) |
| Manage freshness / writing / retries | Cache-Aside / Outbox / Saga / CQRS / Retry | [Choose by task and failure](distributed-systems.md#quick-choice) |

[Architecture](../README.md) · [Principles](../principles.md) · [SOLID](../solid.md)
[Complete examples](#complete-examples) · [Partial failure](#data-and-partial-failure) · [Mistakes](#common-mistakes) · [Sources](#sources)

<a id="базовый-уровень"></a>

In Python, Strategy can be a callable, Adapter a conversion function, and Factory a composition function.
For one simple variant, a direct function without a class hierarchy is often sufficient.

<a id="средний-уровень"></a>

<a id="полные-примеры"></a>
## Complete examples

| Details needed | Complete page | Tested behavior |
| --- | --- | --- |
| Combine Strategy, Adapter, Decorator, and Factory | [Shipping](code-examples.md#complete-strategy-adapter-and-decorator-example) | Two rates, units, rounding, results, and errors |
| Notify local listeners | [Observer](code-examples.md#observer-subscriptions-unsubscribe-and-listener-errors) | Order, unsubscribe, stopping on error |
| Reserve through a command | [Command](code-examples.md#command-request-handler-and-local-replay) | Validation, result, replay, and ID conflict |

<a id="продвинутый-уровень"></a>

<a id="данные-и-частичный-отказ"></a>
## Data and partial failure

Before splitting into processes, define data ownership, possible outcomes, and the retry protocol.
The [distributed scenario cards](distributed-systems.md) show each guarantee and its boundary.
The [complete Outbox example](outbox-example.md#complete-outbox-example-and-duplicate-publication) shows local-write rollback and duplicate publication.
For a stuck process, assign ownership of monitoring and recovery.

<a id="частые-ошибки"></a>
## Common mistakes

| Confusion | Clarification |
| --- | --- |
| Ports & Adapters = microservices | Application boundaries and deployment units are separate axes |
| `@decorator` = any Decorator pattern | A syntactic wrapper and the object pattern share an idea but are distinct |
| Factory always means Abstract Factory / Factory Method | A simple composition function need not implement these GoF patterns |
| CQRS = Event Sourcing | Separating read/write models does not require events as the source of truth |
| Retry means repeating any error | Classification, a total time limit, and safe retry semantics are required |

<a id="границы-примеров"></a>
## Example boundaries

The [code pattern examples](code-examples.md) run locally in one process.
The [learning Outbox](outbox-example.md#complete-outbox-example-and-duplicate-publication) uses an in-memory database and a list in place of a broker.
Networking, recovery after process termination, load, and concurrency require separate decisions.

<a id="источники"></a>
## Sources

- [GoF Design Patterns publisher page](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780201633610).
- [Cockburn, Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/).
- [Microsoft architecture pattern catalog](https://learn.microsoft.com/en-us/azure/architecture/patterns/).
