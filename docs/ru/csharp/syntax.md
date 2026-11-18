# Синтаксис C# и стандартная библиотека

[C#](README.md) · [English](../../en/csharp/syntax.md)

Используйте карточки с C# 14 и .NET 10. Файл проекта SDK и команды оболочки доступны в разделе [«Первый запуск»](README.md#первый-запуск).

Запускайте каждый фрагмент для `Program.cs` отдельно. Вставьте его в [консольный проект `net10.0`](tooling-and-testing.md#project-templates) и выполните `dotnet run` из каталога проекта.

| Задача | Приём | Пример |
| --- | --- | --- |
| Проверить ввод и выбрать ветвь | `TryParse`, `if`, выражение `switch`, сопоставление с образцом | [Типы и управление потоком](#types-and-control-flow) |
| Вынести повторяемую операцию | Методы, локальные функции, параметры типов | [Функции](#functions) |
| Описать данные и поведение | Классы, записи, структуры, интерфейсы, свойства | [Данные и контракты](#data-and-contracts) |
| Найти или преобразовать элементы | `Dictionary`, `HashSet`, LINQ | [Коллекции](#collections) |
| Прочитать файл с поддержкой отмены | `Task<T>`, `await`, `CancellationToken`, `using` | [Асинхронный ввод-вывод и освобождение ресурсов](#async-io-and-cleanup) |
| Найти API для повседневных задач | Базовые библиотеки в `System` | [Стандартная библиотека](#standard-library) |

<a id="types-and-control-flow"></a>

## Типы и управление потоком

Выберите тип, который соответствует данным. `int` хранит 32-битные целые числа. `long` хранит 64-битные целые числа. Используйте `double` для приближённых вычислений с плавающей точкой. Используйте `decimal` для десятичных значений, например цен. Используйте `bool` для условий, а `string` для строк. Для локальной переменной с `var` компилятор выводит статический тип по начальному значению.

Фрагмент для `Program.cs`. Преобразуйте строку в число и определите категорию числа выражением `switch`.

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

Программа выводит `42: pass`. Метод `TryParse` обрабатывает неверный формат и переполнение. Образец отдельно проверяет допустимый диапазон оценки. Используйте `foreach` для обхода элементов. Используйте `for`, если операции нужен индекс.

Если включены предупреждения о `null`, тип `string?` допускает отсутствие значения. Компилятор предупреждает о возможном обращении через ссылку со значением `null`. Фрагмент для переменной `string? label`:

```csharp
string displayName = label?.Trim() ?? "untitled";
```

Если `label` равна `null`, результат равен `untitled`. Если строка состоит только из пробельных символов, результат пуст. Добавьте отдельное правило, если пустой строке тоже нужно значение по умолчанию.

<a id="functions"></a>

## Функции

Локальная функция из [первой программы](../../../examples/csharp/basics/Program.cs). Импортируйте `System.Collections.Generic` для `List<T>`.

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

Для списка `2`, `5`, `3` и порога `3` результат равен `2`. Локальная функция с модификатором `static` не может захватывать переменные из внешней области. По умолчанию аргументы передаются по значению. Для `List<int>` значением служит ссылка на тот же список. Через эту ссылку метод может менять список.

| Задача | Форма | Следствие |
| --- | --- | --- |
| Вызвать операцию у объекта | Метод экземпляра | Метод использует состояние объекта |
| Применить логику к разным типам элементов | `static T FirstOr<T>(IReadOnlyList<T> items, T fallback)` | Одна сигнатура для разных типов элементов |
| Задать аргумент по умолчанию | `int minimum = 3` в списке параметров | Аргумент можно опустить при вызове |
| Вернуть значение через аргумент | `out int score` | Метод присваивает значение переменной |
| Изменить переменную вызывающего кода | `ref` в объявлении и вызове | До вызова переменной нужно присвоить значение |

<a id="data-and-contracts"></a>

## Данные и контракты

Фрагмент для `Program.cs`. Создайте запись и скопируйте её с изменённым свойством.

```csharp
using System;

var product = new Product("Pen", 2m);
var discounted = product with { Price = 1m };
Console.WriteLine(discounted == new Product("Pen", 1m));

public sealed record Product(string Name, decimal Price);
```

Программа выводит `True`. Компилятор создаёт для записи свойства и равенство по значению. Выражение `with` делает поверхностную копию. Исходная запись и копия могут ссылаться на один изменяемый объект.

| Задача | Конструкция | Условие |
| --- | --- | --- |
| Сохранить идентичность и управлять состоянием | `class`, конструктор, свойства | Экземпляры класса имеют ссылочную семантику |
| Сравнить данные по значению | `record` или `record struct` | Равенство членов зависит от их типов |
| Представить небольшое значение | `readonly struct` | Присваивание копирует значение. Учтите поведение `default`. |
| Описать контракт для разных реализаций | `interface` | См. [композицию и тестирование](practice.md#patterns) |
| Сгруппировать типы и ограничить доступ | `namespace`, `using`, `public`, `internal`, `private`, `protected` | `internal` по умолчанию ограничивает доступ сборкой. `protected` разрешает доступ из производных типов. |

Используйте `{ get; set; }` для изменяемого свойства. Используйте `{ get; init; }`, если свойство задаётся при инициализации. В C# 14 доступно условное присваивание через `?.`. Если у объекта `draft` есть изменяемое свойство `Name`, выражение `draft?.Name = "Pen"` присваивает имя только при наличии объекта.

<a id="collections"></a>

## Коллекции

| Задача | Тип или API | Условие |
| --- | --- | --- |
| Хранить фиксированное число элементов | `T[]` | Длина задаётся при создании. Индексы начинаются с 0. |
| Добавить элемент или обратиться по индексу | `List<T>` | Используйте индексы от 0 до `Count - 1` |
| Прочитать значение по ключу | `scores.TryGetValue("Ada", out int score)` | [Проверить наличие ключа](#try-get-value) |
| Проверить наличие или убрать дубли | `names.Contains("Ada")`, `names.Add("Ada")` | Для `HashSet<string> names` метод `Add` возвращает `false`, если такое имя уже есть. Совпадение определяет правило равенства множества. |
| Отфильтровать, преобразовать или агрегировать | LINQ `Where`, `Select`, `Count` | Часть операторов выполняется при обходе запроса |

<a id="try-get-value"></a>

### Получить оценку из словаря

Самостоятельный фрагмент для `Program.cs`. У Ады записана оценка `0`.

```csharp
using System;
using System.Collections.Generic;

var scores = new Dictionary<string, int> { ["Ada"] = 0 };
if (scores.TryGetValue("Ada", out int score))
{
    Console.WriteLine(score);
}
else
{
    Console.WriteLine("Missing key");
}
```

Программа выводит `0`. Замените `"Ada"` на `"Max"` только в строке вызова. Теперь программа выведет `Missing key`. Метод возвращает `true`, если нашёл ключ. Для отсутствующего ключа метод возвращает `false` и записывает в `score` значение по умолчанию для `int`, то есть `0`.

### Отобрать оценки и отсортировать результат

Фрагмент для `Program.cs`. Сохраните подходящие оценки в отсортированный массив.

```csharp
using System;
using System.Collections.Generic;
using System.Linq;

List<int> scores = new() { 2, 5 };
scores.Add(3);
int[] passing = scores.Where(score => score >= 3).OrderBy(score => score).ToArray();
Console.WriteLine(string.Join(", ", passing));
```

Программа выводит `3, 5`. Операторы `Where` и `OrderBy` формируют запрос с отложенным выполнением. Метод `ToArray` выполняет запрос и выделяет массив. Если нужно только количество, вызовите `scores.Count(score => score >= 3)`. Подсчёт обойдётся без сортировки и массива.

<a id="async-io-and-cleanup"></a>

## Асинхронный ввод-вывод и освобождение ресурсов

Фрагмент метода. Импортируйте `System.IO`, `System.Threading` и `System.Threading.Tasks`. Передайте путь к существующему текстовому файлу и токен отмены вызывающего кода.

```csharp
static async Task<string> ReadTextAsync(string path, CancellationToken cancellationToken)
{
    using var reader = File.OpenText(path);
    return await reader.ReadToEndAsync(cancellationToken);
}
```

Вызывающий код получает текст через `await`. Если чтение требует ожидания, `await` освобождает поток для другой работы. Инструкция `using` освобождает ресурс при выходе из метода, в том числе при ошибке. Используйте `await using` для асинхронного освобождения ресурса с интерфейсом `IAsyncDisposable`. Передавайте токен отмены в вызовы, которые его поддерживают.

<a id="standard-library"></a>

## Стандартная библиотека

| Задача | API | Выбор |
| --- | --- | --- |
| Прочитать файл и соединить части пути | `var path = Path.Combine("data", "scores.json");` · `using var stream = File.OpenRead(path);` | Импортируйте `System.IO`. Файл должен существовать. Читайте его потоком, если он велик. |
| Записать и прочитать JSON | `JsonSerializer.Serialize(new[] { 2, 5 })`, `JsonSerializer.Deserialize<int[]>("[2,5]")` | Импортируйте `System.Text.Json`. Для внешних данных задайте правила для имён полей, отсутствующих значений и ошибок. |
| Получить текст по HTTP | `string body = await client.GetStringAsync(uri, token);` | Передайте адрес и `CancellationToken`. Используйте долгоживущий `HttpClient` или настройте [`IHttpClientFactory`](practice.md#patterns). |
| Получить момент времени через час | `DateTimeOffset.UtcNow + TimeSpan.FromHours(1)` | Результат имеет смещение UTC. Храните идентификатор часового пояса отдельно, если нужны его правила. |
| Преобразовать последовательность в памяти | `System.Linq.Enumerable` | Сохраните результат один раз, если нужен снимок данных |
| Отменить ввод-вывод или дождаться задач | Передайте `CancellationToken` операции. Для массива `Task[] tasks` вызовите `await Task.WhenAll(tasks)`. | Импортируйте `System.Threading.Tasks` для `Task`. Ограничьте число запущенных операций отдельно. |

<a id="common-mistakes"></a>

## Типичные ошибки

| Симптом | Действие |
| --- | --- |
| `scores[scores.Count]` вызывает исключение | Используйте последний допустимый индекс. Перед обращением проверьте, что список содержит элемент. |
| Значение отсутствует во время выполнения | Проверьте значение. Оператор `!` только подавляет предупреждения. |
| Отложенный запрос видит поздние изменения или повторяет дорогую работу | Сохраните результат один раз там, где нужен снимок данных |
| `.Result` или `.Wait()` блокирует поток | Используйте `await` в цепочке асинхронных вызовов |
| Блок `catch` скрывает ошибку или меняет трассировку стека | Перехватывайте исключение там, где можете его обработать. Используйте `throw;` для повторного выброса с исходной трассировкой. |

## Источники

- [Поиск ключа через Dictionary.TryGetValue в .NET 10](https://learn.microsoft.com/ru-ru/dotnet/api/system.collections.generic.dictionary-2.trygetvalue?view=net-10.0).
- [Справочник языка C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/) и [изменения C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14).
- [Параметры и аргументы](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/method-parameters), [записи](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record) и [ссылочные типы с поддержкой `null`](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/null-safety/nullable-reference-types).
- [Коллекции](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/collections), [выполнение запросов LINQ](https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries) и [асинхронные сценарии](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios).
- [Справочник API .NET 10](https://learn.microsoft.com/en-us/dotnet/api/?view=net-10.0) и [`StreamReader.ReadToEndAsync`](https://learn.microsoft.com/en-us/dotnet/api/system.io.streamreader.readtoendasync?view=net-10.0).
