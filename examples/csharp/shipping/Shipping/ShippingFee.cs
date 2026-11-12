using System;

namespace Shipping;

public static class ShippingFee
{
    public static int Calculate(int orderTotalInCents)
    {
        ArgumentOutOfRangeException.ThrowIfNegative(orderTotalInCents);
        return orderTotalInCents >= 5_000 ? 0 : 500;
    }
}
