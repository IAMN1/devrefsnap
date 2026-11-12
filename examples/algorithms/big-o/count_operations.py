def count_items(items):
    operations = 0
    for item in items:
        operations += 1
    return operations


def count_pairs(items):
    operations = 0
    for first in items:
        for second in items:
            operations += 1
    return operations


if __name__ == "__main__":
    print("n linear quadratic")
    for n in (4, 8, 16):
        items = range(n)
        print(n, count_items(items), count_pairs(items))
