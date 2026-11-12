using System;
using Xunit;

namespace Shipping.Tests;

public sealed class ShippingFeeTests
{
    [Theory]
    [InlineData(0, 500)]
    [InlineData(4_999, 500)]
    [InlineData(5_000, 0)]
    [InlineData(7_500, 0)]
    public void Calculate_ReturnsExpectedFee(int orderTotalInCents, int expectedFee)
    {
        int actualFee = ShippingFee.Calculate(orderTotalInCents);

        Assert.Equal(expectedFee, actualFee);
    }

    [Fact]
    public void Calculate_RejectsNegativeTotal()
    {
        var exception = Assert.Throws<ArgumentOutOfRangeException>(
            () => ShippingFee.Calculate(-1));

        Assert.Equal("orderTotalInCents", exception.ParamName);
    }
}
