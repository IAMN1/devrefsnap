#include "score-summary.hpp"

#include <gtest/gtest.h>

#include <array>
#include <stdexcept>

TEST(ScoreSummaryTest, CountsScoresAtOrAboveMinimum)
{
    constexpr std::array scores{55, 60, 95};
    const ScoreSummary summary = summarize_scores(scores, 60);
    EXPECT_EQ(summary.total, 3u);
    EXPECT_EQ(summary.at_least_minimum, 2u);
}

TEST(ScoreSummaryTest, AcceptsEmptyInput)
{
    const ScoreSummary summary = summarize_scores({}, 60);
    EXPECT_EQ(summary.total, 0u);
    EXPECT_EQ(summary.at_least_minimum, 0u);
}

TEST(ScoreSummaryTest, AcceptsBothEndpoints)
{
    constexpr std::array scores{0, 100};
    EXPECT_EQ(summarize_scores(scores, 0).at_least_minimum, 2u);
    EXPECT_EQ(summarize_scores(scores, 100).at_least_minimum, 1u);
}

TEST(ScoreSummaryTest, RejectsMinimumOutsideRange)
{
    EXPECT_THROW(summarize_scores({}, -1), std::invalid_argument);
    EXPECT_THROW(summarize_scores({}, 101), std::invalid_argument);
}

TEST(ScoreSummaryTest, RejectsInvalidScoreEvenBelowMinimum)
{
    constexpr std::array scores{95, -1};
    EXPECT_THROW(summarize_scores(scores, 60), std::invalid_argument);
}

TEST(ScoreSummaryTest, RejectsScoreAboveMaximum)
{
    constexpr std::array scores{101};
    EXPECT_THROW(summarize_scores(scores, 60), std::invalid_argument);
}
