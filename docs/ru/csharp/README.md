# C#

[Каталог](../README.md) · [English](../../en/csharp/README.md)

Соберите первую программу на C# или найдите конструкцию языка, команду для пакета или приём тестирования. Исполняемые примеры используют .NET 10 и C# 14.

| Задача | Приём | Пример |
| --- | --- | --- |
| Запустить первую программу | .NET SDK, `dotnet build`, `dotnet run` | [Первый запуск](#первый-запуск) |
| Разобрать ввод, описать данные или выполнить асинхронный ввод-вывод | Типы, сопоставление с образцом, LINQ, `async` / `await` | [Синтаксис и стандартная библиотека](syntax.md) |
| Создать проект или добавить зависимость | `dotnet new`, NuGet, `PackageReference` | [Проекты и пакеты](tooling-and-testing.md#packages) |
| Проверить бизнес-правило | xUnit v3 и `dotnet test` | [Исполняемый пример с тестами](tooling-and-testing.md#tests) |
| Выбрать стек для нового проекта | Веб, данные, рабочий стол, игры, облако, мобильные и нативные приложения | [Области применения](practice.md#application-areas) |
| Разделить обязанности компонентов | Внедрение зависимостей, композиция, время жизни | [Паттерны и практики](practice.md#patterns) |

## Первый запуск

Установите [.NET SDK 10](https://dotnet.microsoft.com/download/dotnet/10.0). Проверьте командой `dotnet --version`, что оболочка использует SDK версии `10.0.x`. Команды рассчитаны на Bash или Zsh.

SDK включает компилятор, инструменты сборки и среду выполнения. [Файл проекта](../../../examples/csharp/basics/basics.csproj) задаёт целевую платформу `net10.0`. Для этой платформы компилятор по умолчанию выбирает C# 14. [Полная программа](../../../examples/csharp/basics/Program.cs) использует стандартную библиотеку. Дополнительные пакеты NuGet не требуются. Программа считает элементы списка, которые больше порога или равны ему.

Из корня репозитория соберите проект и запустите программу без аргументов.

```bash
project=examples/csharp/basics/basics.csproj
build_dir=$(mktemp -d) &&
  dotnet build "$project" --artifacts-path "$build_dir" &&
  dotnet run --project "$project" --artifacts-path "$build_dir" --no-build
```

Сборка помещает артефакты во временный каталог. Компилятор создаёт точку входа из инструкций верхнего уровня в `Program.cs`. Список содержит числа `2`, `5` и `3`. При пороге `3` программа выводит следующее сообщение.

```text
Count: 2
```

## Типы и управление потоком

Массив аргументов содержит строки. Программа проверяет ввод через `if` и сравнивает элементы списка с порогом в цикле `foreach`. См. [типы, разбор ввода и управление потоком](syntax.md#types-and-control-flow).

## Функции

Локальная функция `CountAtLeast` принимает список и порог через параметры и возвращает `int`. Модификатор `static` запрещает захватывать локальные переменные из внешней области. См. [функции и передачу параметров](syntax.md#functions).

## Коллекции

Программа добавляет число в список через `List<int>.Add`. См. [массивы, списки, словари, множества и LINQ](syntax.md#collections).

## Типичные ошибки

Проверьте порог 5 и неверный аргумент. Используйте переменные из первого запуска.

```bash
dotnet run --project "$project" --artifacts-path "$build_dir" --no-build -- 5
dotnet run --project "$project" --artifacts-path "$build_dir" --no-build -- wrong
```

Первая команда выводит `Count: 1`. Вторая выводит `Expected one integer threshold or no arguments.` в поток ошибок и завершается с кодом `2`. См. [типичные ошибки с типами, коллекциями и задачами](syntax.md#common-mistakes).

## Источники

- [Обзор выпуска .NET 10](https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-10/overview) и [версия C# по целевой платформе](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning#defaults).
- [Инструкции верхнего уровня](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/program-structure/top-level-statements), [`dotnet build`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-build) и [`dotnet run`](https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-run).
