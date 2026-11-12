# C# syntax and standard library

[C#](README.md) · [Русский](../../ru/csharp/syntax.md)

Use these cards with C# 14 and .NET 10. See [first run](README.md#first-run) for an SDK project and the shell commands.

Run each `Program.cs` excerpt separately. Paste it into a [`net10.0` console project](tooling-and-testing.md#project-templates) and run `dotnet run` from the project directory.

| Task | Technique | Example |
| --- | --- | --- |
| Validate input and choose a branch | `TryParse`, `if`, `switch` expression, patterns | [Types and control flow](#types-and-control-flow) |
| Extract a reusable operation | Methods, local functions, generic parameters | [Functions](#functions) |
| Model data and behavior | Classes, records, structs, interfaces, properties | [Data and contracts](#data-and-contracts) |
| Look up or transform items | `Dictionary`, `HashSet`, LINQ | [Collections](#collections) |
| Read a file and support cancellation | `Task<T>`, `await`, `CancellationToken`, `using` | [Async I/O and cleanup](#async-io-and-cleanup) |
| Find an API for everyday work | Base libraries under `System` | [Standard library](#standard-library) |

## Types and control flow

Choose a type that represents the data. `int` is a 32-bit integer. `long` is a 64-bit integer. Use `double` for approximate floating-point calculations and `decimal` for decimal values such as prices. Use `bool` for conditions and `string` for text. The compiler infers the static type of a local variable declared with `var` from its initializer.

Excerpt for `Program.cs`. Parse a number and classify it with a `switch` expression.

```csharp
using System;

string input = "42";
if (!int.TryParse(input, out int score))
{
    Console.Error.WriteLine("Expected an integer.");
    return 2;
}

var band = score switch
{
    < 0 or > 100 => "out of range",
    >= 40 => "pass",
    _ => "retry"
};

Console.WriteLine($"{score}: {band}");
return 0;
```

The program prints `42: pass`. `TryParse` handles format errors and overflow. The pattern separately checks the allowed score range. Use `foreach` to visit items and `for` when the operation needs an index.

When nullable warnings are enabled, `string?` allows an absent value and the compiler warns about possible unsafe dereferences. A fragment for a nullable `string? label`:

```csharp
string displayName = label?.Trim() ?? "untitled";
```

A null `label` yields `untitled`. A whitespace-only label yields an empty string. Apply a separate rule when blank labels should use the fallback.

## Functions

Local function from [the first program](../../../examples/csharp/basics/Program.cs). Import `System.Collections.Generic` for `List<T>`.

```csharp
static int CountAtLeast(List<int> scores, int minimum)
{
    int count = 0;
    foreach (int score in scores)
    {
        if (score >= minimum)
        {
            ++count;
        }
    }
    return count;
}
```

A list containing `2`, `5`, and `3` gives a count of `2` at a threshold of `3`. A `static` local function cannot capture variables from its enclosing scope. Arguments pass by value by default. For `List<int>`, the value is a reference to the same list, so a method can change that list through the reference.

| Need | Form | Consequence |
| --- | --- | --- |
| Access behavior through an object | Instance method | Uses the object's state |
| Reuse logic across element types | `static T FirstOr<T>(IReadOnlyList<T> items, T fallback)` | One method signature for multiple element types |
| Provide a default argument | `int minimum = 3` in the parameter list | Callers may omit the argument |
| Return a value through an argument | `out int score` | The method assigns the variable |
| Change the caller's variable directly | `ref` at declaration and call | The caller must initialize the variable first |

## Data and contracts

Excerpt for `Program.cs`. Create a data value and make a copy with one changed property.

```csharp
using System;

var product = new Product("Pen", 2m);
var discounted = product with { Price = 1m };
Console.WriteLine(discounted == new Product("Pen", 1m));

public sealed record Product(string Name, decimal Price);
```

The program prints `True`. The compiler generates properties and value equality for this record. A `with` expression makes a shallow copy. Any referenced mutable object can still be shared between the original and the copy.

| Need | Construct | Condition |
| --- | --- | --- |
| Keep identity and manage state | `class`, constructor, properties | Class instances have reference semantics |
| Compare data values | `record` or `record struct` | Member types determine member equality |
| Represent a small value | `readonly struct` | Assignments copy the value. Consider the behavior of `default`. |
| Define a contract for different implementations | `interface` | See [composition and testing](practice.md#patterns) |
| Group types and control access | `namespace`, `using`, `public`, `internal`, `private`, `protected` | `internal` restricts access to the assembly by default. `protected` allows access from derived types. |

Use `{ get; set; }` for a writable property and `{ get; init; }` for one set during initialization. C# 14 adds null-conditional assignment. For a nullable object `draft` with a writable `Name` property, `draft?.Name = "Pen"` assigns the name only when `draft` exists.

## Collections

| Need | Type or API | Condition |
| --- | --- | --- |
| Keep a fixed number of elements | `T[]` | Size is fixed at creation. Indexing starts at 0. |
| Append or access by index | `List<T>` | Use indices from 0 through `Count - 1` |
| Look up by key | `Dictionary<TKey, TValue>`, `TryGetValue` | `TryGetValue` reports missing keys |
| Track membership or remove duplicates | `HashSet<T>` | Equality determines whether two elements are duplicates |
| Filter, project, or aggregate | LINQ `Where`, `Select`, `Count` | Some operators defer execution until enumeration |

Excerpt for `Program.cs`. Take a sorted snapshot of the matching scores.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

List<int> scores = new() { 2, 5 };
scores.Add(3);
int[] passing = scores.Where(score => score >= 3).OrderBy(score => score).ToArray();
Console.WriteLine(string.Join(", ", passing));
```

The program prints `3, 5`. `Where` and `OrderBy` build a deferred query. `ToArray` runs the query and allocates an array. If you only need the count, call `scores.Count(score => score >= 3)` to skip the sort and array.

## Async I/O and cleanup

Method fragment. Import `System.IO`, `System.Threading`, and `System.Threading.Tasks`. Pass the path of an existing text file and the caller's cancellation token.

```csharp
static async Task<string> ReadTextAsync(string path, CancellationToken cancellationToken)
{
    using var reader = File.OpenText(path);
    return await reader.ReadToEndAsync(cancellationToken);
}
```

The caller receives the text by awaiting the task. `await` lets the calling thread continue when the read needs to wait. `using` disposes the reader when the method exits, including on failure. Use `await using` when a resource implements `IAsyncDisposable` and requires asynchronous cleanup. Pass cancellation tokens through calls that support them.

## Standard library

| Task | API | Choice |
| --- | --- | --- |
| Read files and join path components | `System.IO.File`, `Stream`, `Path.Combine` | Stream data when reading the full file would consume too much memory |
| Encode and decode JSON | `System.Text.Json.JsonSerializer` | Decide how to handle names, missing values, and invalid input at the boundary |
| Call an HTTP service | `System.Net.Http.HttpClient` | Reuse the client or configure [`IHttpClientFactory`](practice.md#patterns) |
| Represent an instant with an offset | `DateTimeOffset`, `TimeSpan` | Keep a time zone identifier separately when you need its rules |
| Transform a sequence in memory | `System.Linq.Enumerable` | Materialize once when you need a stable snapshot |
| Cancel I/O and coordinate tasks | `CancellationToken`, `Task.WhenAll` | Limit concurrency when requests compete for a bounded resource |

## Common mistakes

| Symptom | Action |
| --- | --- |
| `scores[scores.Count]` throws | Use the last valid index or check that the list has an element |
| A nullable value is missing at runtime | Check the value. The null-forgiving operator `!` only suppresses warnings. |
| A deferred query observes later changes or repeats expensive work | Materialize once where the caller needs a snapshot |
| `.Result` or `.Wait()` blocks a thread | Use `await` in the async call chain |
| A catch block hides a failure or resets the stack trace | Catch where you can handle the failure. Use `throw;` to rethrow with the original stack trace. |

## Sources

- [C# language reference](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/) and [C# 14 release notes](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14).
- [Parameters and arguments](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/method-parameters), [records](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record), and [nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types).
- [Collections](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/collections), [LINQ execution](https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries), and [async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios).
- [.NET 10 API reference](https://learn.microsoft.com/en-us/dotnet/api/?view=net-10.0) and [`StreamReader.ReadToEndAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.io.streamreader.readtoendasync?view=net-10.0).
