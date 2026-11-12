# C#

[Catalog](../README.md) · [Русский](../../ru/csharp/README.md)

Build your first C# program or look up a language feature, package command, or testing pattern. The runnable examples target .NET 10 with C# 14.

| Task | Technique | Example |
| --- | --- | --- |
| Run your first program | .NET SDK, `dotnet build`, `dotnet run` | [First run](#first-run) |
| Parse input, model data, or handle async I/O | Types, pattern matching, LINQ, `async` / `await` | [Syntax and standard library](syntax.md) |
| Create a project or add a dependency | `dotnet new`, NuGet, `PackageReference` | [Projects and packages](tooling-and-testing.md#packages) |
| Test a business rule | xUnit v3 and `dotnet test` | [Runnable test lab](tooling-and-testing.md#tests) |
| Choose a stack for a new project | Web, data, desktop, games, cloud, mobile, native | [Application areas](practice.md#application-areas) |
| Decide where to split responsibilities | Dependency injection, composition, lifetimes | [Patterns and practices](practice.md#patterns) |

## First run

Install the [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0). Check that `dotnet --version` reports a version in the `10.0.x` series. The shell examples use Bash or Zsh.

The SDK includes the compiler, build tools, and runtime. The [project file](../../../examples/csharp/basics/basics.csproj) targets `net10.0`, which selects C# 14 by default. The [complete program](../../../examples/csharp/basics/Program.cs) uses the standard library and requires no extra NuGet packages. It counts scores that meet or exceed a threshold.

From the repository root, build and run the program with no arguments.

```bash
project=examples/csharp/basics/basics.csproj
build_dir=$(mktemp -d) &&
  dotnet build "$project" --artifacts-path "$build_dir" &&
  dotnet run --project "$project" --artifacts-path "$build_dir" --no-build
```

The build writes its artifacts to the temporary directory. The compiler generates the entry point from the top-level statements in `Program.cs`. The list contains `2`, `5`, and `3`. With the default threshold of `3`, the program prints:

```text
Count: 2
```

## Types and control flow

The argument array contains strings. The program uses `if` to validate the input and `foreach` to check each score against the threshold. See [types, parsing, and control flow](syntax.md#types-and-control-flow).

## Functions

The `static` local function `CountAtLeast` takes the list and threshold as parameters and returns an `int`. See [functions and parameter passing](syntax.md#functions).

## Collections

The program calls `List<int>.Add` to append a score. See [arrays, lists, dictionaries, sets, and LINQ](syntax.md#collections).

## Common mistakes

Reuse the variables from the first run to check an explicit threshold and an invalid argument.

```bash
dotnet run --project "$project" --artifacts-path "$build_dir" --no-build -- 5
dotnet run --project "$project" --artifacts-path "$build_dir" --no-build -- wrong
```

The first command prints `Count: 1`. The second writes `Expected one integer threshold or no arguments.` to standard error and exits with code `2`. See [common mistakes with types, collections, and tasks](syntax.md#common-mistakes).

## Sources

- [.NET 10 release overview](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview) and [default C# version by target framework](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning#defaults).
- [Top-level statements](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/program-structure/top-level-statements), [`dotnet build`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build), and [`dotnet run`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run).
