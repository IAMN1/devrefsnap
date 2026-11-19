using System.Net;
using System.Text.Json;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace Shipping.Api.Tests;

public sealed class ShippingQuoteTests(WebApplicationFactory<Program> factory)
    : IClassFixture<WebApplicationFactory<Program>>
{
    [Theory]
    [InlineData(4999, 500)]
    [InlineData(5000, 0)]
    public async Task ValidTotalReturnsShippingFee(int total, int expectedFee)
    {
        using var client = factory.CreateClient();
        var token = TestContext.Current.CancellationToken;
        using var response = await client.GetAsync($"/shipping/quote?orderTotalInCents={total}", token);

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.Equal("application/json", response.Content.Headers.ContentType?.MediaType);
        using var body = JsonDocument.Parse(await response.Content.ReadAsStringAsync(token));
        Assert.Equal(expectedFee, body.RootElement.GetProperty("feeInCents").GetInt32());
    }

    [Fact]
    public async Task NegativeTotalReturnsBadRequest()
    {
        using var client = factory.CreateClient();
        var token = TestContext.Current.CancellationToken;
        using var response = await client.GetAsync("/shipping/quote?orderTotalInCents=-1", token);

        Assert.Equal(HttpStatusCode.BadRequest, response.StatusCode);
        using var body = JsonDocument.Parse(await response.Content.ReadAsStringAsync(token));
        Assert.Equal("Order total must be non-negative.", body.RootElement.GetProperty("error").GetString());
    }
}
