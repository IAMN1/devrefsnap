#include <cstddef>
#include <iostream>
#include <vector>

std::size_t count_at_least(const std::vector<int>& scores, int minimum)
{
    std::size_t count = 0;
    for (int score : scores) {
        if (score >= minimum) {
            ++count;
        }
    }
    return count;
}

int main()
{
    std::vector<int> scores{2, 5};
    scores.push_back(3);
    std::cout << "Count: " << count_at_least(scores, 3) << '\n';
    return 0;
}
