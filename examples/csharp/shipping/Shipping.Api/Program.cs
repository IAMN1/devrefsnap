using Shipping;

var app = WebApplication.CreateBuilder(args).Build();
app.MapGet("/shipping/quote", QuoteShipping);
app.Run();

static IResult QuoteShipping(int orderTotalInCents)
{
    if (orderTotalInCents < 0)
    {
        return Results.BadRequest(new { error = "Order total must be non-negative." });
    }

    int feeInCents = ShippingFee.Calculate(orderTotalInCents);
    return Results.Ok(new { feeInCents });
}

// WebApplicationFactory uses the entry point to start the application in tests.
public partial class Program { }
