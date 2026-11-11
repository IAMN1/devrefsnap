<a id="проверять-инварианты-и-контракты"></a>
# Test invariants and contracts

[Русский](../../ru/architecture/contracts.md)

This page contains two complete local examples.
The first reserves stock.
The second substitutes a price source.
Use the examples to test rejection without state mutation or implementation replacement under a shared contract.

| Task | Scenario | Checks |
| --- | --- | --- |
| Protect stock | [Stock](#reserve-stock) | Success, invalid input, shortage, state preservation on rejection |
| Replace a price source | [PriceReader](#substitute-a-price-source) | Result, KeyError, repeated reading, incompatible implementation detection |

[Principles](principles.md#contracts-and-invariants) · [SOLID](solid.md) · [Architecture](README.md)

The invariant example is **intermediate level**.
The advanced example covers substitution semantics.
**Prerequisites** include functions, classes, exceptions, assert, and Python structural typing.

The examples use Python 3.14 and synthetic in-memory data.
They run in one thread without a database or network.

<a id="резерв-остатка"></a>
## Reserve stock

**Intermediate level.** Initial stock must be a nonnegative integer.
The quantity to reserve must be a positive integer.
Stock remains unchanged on rejection.
`bool` is deliberately disallowed as a quantity, although Python treats `bool` as an `int` subclass.

The complete example requires no dependencies.
Save the code as `invariants.py`.
Run `python3.14 invariants.py`.

[`architecture/invariants.py`](../../../examples/architecture/invariants.py)

The result is `OK: successful reservation, invariant and unchanged state on refusal`.
The example includes successful reservation and rejections for `0`, `True`, insufficient stock, and invalid initial stock.

`_available` denotes an internal API convention.
The field name does not prevent intentional access.
Returning a mutable collection can also expose a way around an invariant.
Choose a copy, immutable view, or explicit operation according to requirements.
Concurrent database reservation requires a separate transaction or protocol.

<a id="подстановка-источника-цен"></a>
## Substitute a price source

**Advanced level.** The snapshot contract defines a known `book` price as a nonnegative integer in illustrative cents.
An unknown `sku` raises `KeyError`.
Repeated snapshot reads preserve the price.
`quote` accepts a positive integer quantity.
The contract captures the consumer's agreement beyond the signature.

The complete example requires no pip installation.
Save the code as `solid-contract.py`.
Run `python3.14 solid-contract.py`.

[`architecture/solid-contract.py`](../../../examples/architecture/solid-contract.py)

The result is `OK: consumer contract, valid substitution and incompatible implementation detected`.
The example includes the price `2400`, rejection of quantity `0`, successful substitution, and detection of an incorrect error.

`Protocol` describes structural typing for static checking.
Annotations do not automatically enforce the agreement at runtime.
`runtime_checkable` checks for attributes.
It does not check method semantics or signatures.
The example compares implementation behavior at runtime.
For type checking, use a separate static analyzer.
A finite set of checks does not prove substitutability for all inputs and implementations.

<a id="возможное-размещение-по-модулям"></a>
### Possible module layout

The tree shows possible source files for an expanded example.
These files are unnecessary for running the code above.
A short script can keep the roles together.

```text
pricing/
├── contracts.py   # PriceReader: contract required by the consumer
├── quote.py       # quote: calculation rule, imports PriceReader
├── snapshot.py    # SnapshotPrices: local source
└── main.py        # composition: creates SnapshotPrices and passes it to quote
```

The [DIP diagram](solid.md#d--dependency-direction-and-di-as-a-passing-mechanism) shows code dependencies separately.
`reader.price()` calls a method on the supplied object.
For this call, `quote` does not need to import the object's class.
When replacing the snapshot with a real database, align error behavior.
Align transactions, `NULL`, and data freshness.
A snapshot and an always-current price define different contracts.

<a id="источники"></a>
## Sources

- [Python 3.14 Protocol](https://docs.python.org/3.14/library/typing.html#typing.Protocol) and [PEP 544](https://peps.python.org/pep-0544/) cover structural typing and runtime-checking boundaries.
- [Liskov / Wing, A Behavioral Notion of Subtyping](https://www.cs.cmu.edu/~wing/publications/LiskovWing94.pdf) covers behavioral contracts.
- [Robert C. Martin, SRP](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) covers reasons for change.
