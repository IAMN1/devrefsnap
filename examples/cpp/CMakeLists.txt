cmake_minimum_required(VERSION 3.20)
project(score_count LANGUAGES CXX)

set(CMAKE_CXX_EXTENSIONS OFF)

add_library(score-summary STATIC score-summary.cpp)
target_compile_features(score-summary PUBLIC cxx_std_20)
target_include_directories(score-summary PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

add_executable(score-count score-count.cpp)
target_link_libraries(score-count PRIVATE score-summary)

include(CTest)
if(BUILD_TESTING)
    find_package(GTest 1.17.0 EXACT CONFIG REQUIRED)
    add_executable(score-summary-test score-summary-test.cpp)
    target_link_libraries(score-summary-test PRIVATE score-summary GTest::gtest_main)
    include(GoogleTest)
    gtest_discover_tests(score-summary-test)
endif()
