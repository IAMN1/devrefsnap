#pragma once

#include <cstddef>
#include <span>

struct ScoreSummary {
    std::size_t total{};
    std::size_t at_least_minimum{};
};

// Scores and minimum must be in [0, 100]. Otherwise, throws std::invalid_argument.
ScoreSummary summarize_scores(std::span<const int> scores, int minimum);
