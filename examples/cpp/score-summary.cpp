#include "score-summary.hpp"

#include <stdexcept>

namespace {

bool is_valid_score(int score)
{
    return score >= 0 && score <= 100;
}

}

ScoreSummary summarize_scores(std::span<const int> scores, int minimum)
{
    if (!is_valid_score(minimum)) {
        throw std::invalid_argument{"minimum must be in [0, 100]"};
    }

    ScoreSummary summary{.total = scores.size()};
    for (int score : scores) {
        if (!is_valid_score(score)) {
            throw std::invalid_argument{"each score must be in [0, 100]"};
        }
        if (score >= minimum) {
            ++summary.at_least_minimum;
        }
    }
    return summary;
}
