#include <stddef.h>
#include <stdio.h>

static size_t count_at_least(const int *scores, size_t length, int minimum)
{
    size_t count = 0;
    for (size_t i = 0; i < length; ++i) {
        if (scores[i] >= minimum) {
            ++count;
        }
    }
    return count;
}

int main(void)
{
    const int scores[] = {2, 5, 3};
    const size_t length = sizeof scores / sizeof scores[0];
    printf("Count: %zu\n", count_at_least(scores, length, 3));
    return 0;
}
