using Microsoft.EntityFrameworkCore;

namespace Orders.Api;

public sealed class Order
{
    public int Id { get; set; }
    public int OrderTotalInCents { get; init; }
    public int FeeInCents { get; init; }
}

public sealed class OrdersDb(DbContextOptions<OrdersDb> options) : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
}
