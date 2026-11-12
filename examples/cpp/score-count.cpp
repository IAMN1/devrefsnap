#include "score-summary.hpp"

#include <charconv>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <system_error>
#include <vector>

namespace {

int parse_integer(std::string_view text)
{
    const char* end = text.data() + text.size();
    int value{};
    const auto [next, error] = std::from_chars(text.data(), end, value);
    if (error != std::errc{} || next != end) {
        throw std::invalid_argument{"expected an integer argument"};
    }
    return value;
}

}

int main(int argc, char* argv[])
{
    if (argc < 2) {
        std::cerr << "Usage: score-count <minimum> [score ...]\n";
        return 2;
    }

    try {
        const int minimum = parse_integer(argv[1]);
        std::vector<int> scores;
        for (int index = 2; index < argc; ++index) {
            scores.push_back(parse_integer(argv[index]));
        }
        const ScoreSummary summary = summarize_scores(scores, minimum);
        std::cout << summary.at_least_minimum << " of " << summary.total << '\n';
    } catch (const std::invalid_argument& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 2;
    }
    return 0;
}
