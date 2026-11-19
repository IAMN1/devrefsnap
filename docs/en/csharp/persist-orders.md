# Save an order in SQLite and read it after a .NET service restart

[C#](README.md) · [Русский](../../ru/csharp/persist-orders.md) · [Your first HTTP service](first-http-service.md)

The first service calculated a shipping fee. Now a client can submit a 4999-cent order, get its ID, and come back for the result. You will stop the entire process and read the order through a new one. Both processes use the same SQLite file.

| Task | Expected result |
| --- | --- |
| [Create an order](#create-order) | `201 Created`, a 500-cent shipping fee, and the order URL in the `Location` header |
| [Read the order after restarting](#restart) | `200 OK` with the same ID, order total, and shipping fee |
| [Look up an unknown ID](#missing-order) | `404 Not Found` |

## Prepare a practice database

You need .NET SDK 10.0.x, Bash or Zsh, and `curl`. The first run needs access to NuGet. The [service project](../../../examples/csharp/shipping/Orders.Api/Orders.Api.csproj) references the `Microsoft.EntityFrameworkCore.Sqlite` 10.0.15 provider. SQLite runs inside the application process, so there is no separate database server to start.

In the first terminal, go to the repository root. Run this block **once**. It creates a separate directory and prints the path to your practice database. Keep that path for the rest of the exercise.

```bash
orders_dir=$(mktemp -d)
orders_project=examples/csharp/shipping/Orders.Api
export ConnectionStrings__Orders="Data Source=$orders_dir/orders.db"
printf '%s\n' "$orders_dir/orders.db"
```

Start the service in the same terminal. The double underscore in the environment variable sets the .NET configuration key `ConnectionStrings:Orders`. The service opens that file and creates the `Orders` table on the first run.

```bash
dotnet run --project "$orders_project" --no-launch-profile -- --urls http://127.0.0.1:5081
```

Wait for `Now listening on: http://127.0.0.1:5081`. If that port is busy, replace `5081` in the launch command and all request URLs.

<a id="create-order"></a>

## Create an order and get its URL

In a second terminal, send the JSON below. With `-d`, curl sends a `POST` request. The `-i` option displays the headers along with the response body.

```bash
curl -i -H 'Content-Type: application/json' -d '{"orderTotalInCents":4999}' http://127.0.0.1:5081/orders
```

For the first order in a fresh database, the response includes the following lines. Other headers are omitted.

```http
HTTP/1.1 201 Created
Location: /orders/1

{"id":1,"orderTotalInCents":4999,"feeInCents":500}
```

The database assigned the `id`. The client supplied only the total. The service calculated shipping with the same [rule](../../../examples/csharp/shipping/Shipping/ShippingFee.cs) as the first lesson. Keep the path from `Location`. Each successful `POST` creates a separate order with its own ID.

<a id="restart"></a>

## Stop the process and read the same order

Press `Ctrl+C` in the first terminal. Wait for the shell prompt. Repeat only the launch command. Repeating the entire setup block would point the service at a different database file.

```bash
dotnet run --project "$orders_project" --no-launch-profile -- --urls http://127.0.0.1:5081
```

Once the service is listening, switch back to the second terminal. Request the path from your `Location` header. The example uses `/orders/1`.

```bash
curl -i http://127.0.0.1:5081/orders/1
```

Expect `200 OK` and the original body, `{"id":1,"orderTotalInCents":4999,"feeInCents":500}`. You never submitted another order between runs. The new process read the saved row from the file.

<a id="missing-order"></a>

## Look up an order that does not exist

In the fresh database containing just one order, request a different ID.

```bash
curl -i http://127.0.0.1:5081/orders/999
```

The service returns `404 Not Found`. If you get this response for an order you created, check the ID against `Location` and compare the database path with the one from the first run.

You can also check input validation. Sending a negative total or omitting `orderTotalInCents` returns `400 Bad Request`. The handler ends the request before adding an order.

When you finish, stop the service with `Ctrl+C`. If you are done with the practice data, delete the temporary directory after shutdown. Deleting it erases the orders stored there.

## How the row survives a restart

The [model and context](../../../examples/csharp/shipping/Orders.Api/OrdersDb.cs) map the `Order` class to the `Orders` table. The `OrdersDb` context tracks object changes during a request. The SQLite provider translates EF Core operations into SQL. The [POST handler](../../../examples/csharp/shipping/Orders.Api/Program.cs) performs these three operations:

```csharp
db.Orders.Add(order);
await db.SaveChangesAsync(token);
return Results.Created($"/orders/{order.Id}", order);
```

`Add` marks the new object for insertion. During `SaveChangesAsync`, EF Core writes the row and obtains its key. Only after the write succeeds does the handler return `201` with the key in the URL. For a `GET` request, the application receives a new context and looks up the row by its primary key. `AsNoTracking()` suits this read-only lookup.

At startup, `EnsureCreatedAsync()` creates the schema in an empty database. This suits a practice database with a fixed model. To evolve an existing schema and keep its data, use EF Core migrations. [SQLite provider](https://learn.microsoft.com/en-us/ef/core/providers/sqlite/) · [Schema creation](https://learn.microsoft.com/en-us/ef/core/managing-schemas/ensure-created) · [Migrations](https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/)
