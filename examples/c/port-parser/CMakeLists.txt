cmake_minimum_required(VERSION 3.24)
project(port_parser LANGUAGES C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(port_parser STATIC port.c)
target_include_directories(port_parser PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")

add_executable(port-check main.c)
target_link_libraries(port-check PRIVATE port_parser)

include(CTest)
if(BUILD_TESTING)
    include(FetchContent)
    FetchContent_Declare(
        unity
        URL https://codeload.github.com/ThrowTheSwitch/Unity/tar.gz/refs/tags/v2.7.0
        URL_HASH SHA256=e84eb301ca7967831e68b1728f911e87fa2d345d8ddb64f897bc2f2ee24a321c
        TLS_VERIFY ON
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
    FetchContent_MakeAvailable(unity)

    add_executable(test_port test_port.c)
    target_link_libraries(test_port PRIVATE port_parser unity::framework)
    add_test(NAME port_parser COMMAND test_port)
endif()
