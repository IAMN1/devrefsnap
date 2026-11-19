using Microsoft.EntityFrameworkCore;
using Orders.Api;
using Shipping;

var builder = WebApplication.CreateBuilder(args);
var connectionString = builder.Configuration.GetConnectionString("Orders")
    ?? throw new InvalidOperationException("Set ConnectionStrings:Orders to the SQLite connection string.");
builder.Services.AddDbContext<OrdersDb>(options => options.UseSqlite(connectionString));

var app = builder.Build();
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<OrdersDb>();
    await db.Database.EnsureCreatedAsync();
}

app.MapPost("/orders", CreateOrder);
app.MapGet("/orders/{id:int}", GetOrder);
await app.RunAsync();

static async Task<IResult> CreateOrder(CreateOrderRequest input, OrdersDb db, CancellationToken token)
{
    if (input.OrderTotalInCents is not int total || total < 0)
    {
        return Results.BadRequest(new { error = "Provide a non-negative integer order total in cents." });
    }

    var order = new Order { OrderTotalInCents = total, FeeInCents = ShippingFee.Calculate(total) };
    db.Orders.Add(order);
    await db.SaveChangesAsync(token);
    return Results.Created($"/orders/{order.Id}", order);
}

static async Task<IResult> GetOrder(int id, OrdersDb db, CancellationToken token)
{
    var order = await db.Orders.AsNoTracking().SingleOrDefaultAsync(order => order.Id == id, token);
    return order is null ? Results.NotFound() : Results.Ok(order);
}

public sealed record CreateOrderRequest(int? OrderTotalInCents);
