<a id="архитектура-и-проектирование"></a>
# Architecture and design

[Русский](../../ru/architecture/README.md)

[Find a technique by task or synonym](../tasks/README.md#architecture-and-design) for boundaries, SOLID, patterns, and retries.

These cheat sheets explain code boundaries, contracts, and application structure.
Start with an observable problem.
The table leads to a card, diagram, and working example.

| Review or task | Destination | What you will find |
| --- | --- | --- |
| Choose a boundary and preserve a rule | [Principles](principles.md) | Cohesion / coupling, invariants, DRY / KISS / YAGNI |
| Make code changes easier | [SOLID](solid.md) | Five cards covering problem → change → before/after |
| Replace an algorithm, wrap a call, translate an API | [Code patterns](patterns/design-patterns.md) | Roles, possible modules, and short calls |
| Organize an application into packages | [Architectural approaches](patterns/architecture-patterns.md#code-organization) | Layered, Vertical Slice, and Ports & Adapters trees |
| Choose release boundaries | [Deployment](patterns/architecture-patterns.md#deployment-boundaries) | Modular Monolith / Microservices |
| Coordinate writes, delivery, and retries | [Data and partial failure](patterns/distributed-systems.md#quick-choice) | Cache-Aside, Outbox, Saga, CQRS, Retry |
| Check an invariant and substitution | [Complete contract examples](contracts.md) | Executable Python covering success, rejection, and state after rejection |

The **pattern catalog** offers a [quick choice](patterns/README.md) and [complete code examples](patterns/code-examples.md).
For **application to a Python project**, follow the route [from choosing a solution to a working package and delivery](../python/architecture/project-design/README.md).
This section covers general techniques.
The separate guide covers Python tools, builds, and environments.

<a id="как-читать-схемы"></a>
## Reading the diagrams

| Representation | Question answered | Meaning of a relationship |
| --- | --- | --- |
| `text` source tree | Where could the roles live? | Directory nesting shows one possible layout |
| Code dependencies | Which part knows another part's API? | Labeled import/contract use. A dotted line can indicate structural conformance |
| Call sequence | Which part calls another at runtime? | Call, response, or message transfer |
| Deployment | Which parts run and release independently? | Local or network connection between executable parts |

One program can contain layers within one process.
A program can call an adapter without importing its class in the application module.
A pattern name does not prescribe a mandatory directory tree.

<a id="маршрут-повторения"></a>
## Review route

Start with an [observable problem](principles.md#cohesion-and-coupling) and a [contract](principles.md#contracts-and-invariants).
Compare [code techniques](patterns/design-patterns.md) and [package structures](patterns/architecture-patterns.md#code-organization) for the same change.
For implementation replacement, open [SOLID](solid.md). For network interactions, open [partial failure](patterns/distributed-systems.md).

A principle helps evaluate a decision.
A pattern offers a known solution structure.
A test checks specific behavior.
A successful local example does not prove an architecture suitable for every load and team.

[All materials](../README.md)
