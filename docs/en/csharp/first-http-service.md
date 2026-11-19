# Your first HTTP service in .NET

[C#](README.md) · [Русский](../../ru/csharp/first-http-service.md)

Run a shipping quote service on your computer. Put an order total in the browser address. For an order worth 4999 cents, the service returns `{"feeInCents":500}`. At 5000 cents, shipping is free.

| Task | Where to start |
| --- | --- |
| Start the service and send your first request | [Run it and inspect the response](#run-service) |
| Find out which code calculates the fee | [Follow a request](#request-path) |
| Check success and validation without starting a server manually | [Run the integration tests](#test-service) |

### What is a service here?

A console program can calculate a result once and exit. This process stays up and serves new requests. Your browser or `curl` acts as the client. ASP.NET Core accepts an HTTP request and passes it to a handler. The client receives a status code and a response body.

In .NET, “service” has several meanings. Here it means a standalone HTTP application. A background service might take jobs from a queue. An injected service is an object the application supplies to other objects. [.NET worker services](https://learn.microsoft.com/en-us/dotnet/core/extensions/workers) · [Dependency injection](practice.md#patterns)

<a id="run-service"></a>

## Run the service and get a response

Install the [.NET 10 SDK](https://dotnet.microsoft.com/download/dotnet/10.0). From the repository directory, check that `dotnet --version` reports `10.0.x`. The SDK includes the Kestrel web server. To see the HTTP status alongside the JSON in a terminal, you also need `curl`.

From the repository root, run the [service project](../../../examples/csharp/shipping/Shipping.Api/Shipping.Api.csproj).

```bash
dotnet run --project examples/csharp/shipping/Shipping.Api --no-launch-profile -- --urls http://127.0.0.1:5080
```

Wait for `Now listening on: http://127.0.0.1:5080`. Keep this terminal open. The address `127.0.0.1` points to your own computer. The number `5080` is the port. If it is busy, pick an available port and replace `5080` in both the launch command and the request URLs.

Open `http://127.0.0.1:5080/shipping/quote?orderTotalInCents=4999` in your browser. To inspect the status and body together, run this command in a second terminal.

```bash
curl -i 'http://127.0.0.1:5080/shipping/quote?orderTotalInCents=4999'
```

Change just the amount at the end of the URL. The same process handles each request.

| Total in cents | HTTP status | Response body |
| ---: | --- | --- |
| 4999 | 200 OK | `{"feeInCents":500}` |
| 5000 | 200 OK | `{"feeInCents":0}` |
| -1 | 400 Bad Request | `{"error":"Order total must be non-negative."}` |

If the browser shows `404` at `/`, visit `/shipping/quote` with the total in the query string. If the connection is refused, check the address and startup message in the first terminal. Press `Ctrl+C` there to stop the service.

<a id="request-path"></a>

## Follow a request through the code

Open [Program.cs](../../../examples/csharp/shipping/Shipping.Api/Program.cs). This service has one endpoint. The HTTP method and path determine which handler receives the request.

```csharp
app.MapGet("/shipping/quote", QuoteShipping);
```

1. At startup, `MapGet` associates `GET /shipping/quote` with the `QuoteShipping` function. The call to `app.Run()` starts the server and waits for shutdown.
2. When a request arrives, ASP.NET Core reads `orderTotalInCents=4999` from the query string and passes the integer `4999` to the handler.
3. The handler checks the total. A negative amount gets an immediate `400` response. For a valid amount, the handler calls [ShippingFee.Calculate](../../../examples/csharp/shipping/Shipping/ShippingFee.cs). That library defines the free shipping threshold.
4. The handler returns `Results.Ok(new { feeInCents })`. ASP.NET Core writes status `200` and serializes the result as JSON. The request calculates a quote without creating an order in a database.

<a id="test-service"></a>

## Test the HTTP contract

The first test run needs access to NuGet. From the repository root, run the following command.

```bash
dotnet test examples/csharp/shipping/Shipping.Api.Tests/Shipping.Api.Tests.csproj
```

Expect three passing test cases. The [HTTP tests](../../../examples/csharp/shipping/Shipping.Api.Tests/ShippingQuoteTests.cs) start the application with `WebApplicationFactory<Program>`. Its client sends requests to an in-memory server, so these tests do not use port `5080`. Returning the correct number under the wrong field name or changing `400` to `200` breaks the contract and causes a test to fail.

The [unit tests](tooling-and-testing.md#tests) call the shipping calculation directly. The integration tests also cover routing, parameter binding, and the HTTP response. The separate `curl` check confirms that Kestrel listens on the chosen port.

Next, [save an order in SQLite and read it after restarting the service](persist-orders.md).

[Minimal APIs in ASP.NET Core 10](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/apis?view=aspnetcore-10.0) · [ASP.NET Core 10 integration tests](https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests?view=aspnetcore-10.0)
