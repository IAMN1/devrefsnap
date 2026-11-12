#include "port.h"

#include <errno.h>
#include <limits.h>
#include <stddef.h>
#include <string.h>
#include <unity.h>

void setUp(void) {}
void tearDown(void) {}

static void test_decimal_port(void)
{
    unsigned int port = 0;
    errno = ERANGE;
    TEST_ASSERT_EQUAL_INT(PORT_OK, parse_port("080", &port));
    TEST_ASSERT_EQUAL_UINT(80, port);
}

static void test_port_bounds(void)
{
    unsigned int port = 0;
    TEST_ASSERT_EQUAL_INT(PORT_OK, parse_port("1", &port));
    TEST_ASSERT_EQUAL_UINT(1, port);
    TEST_ASSERT_EQUAL_INT(PORT_OK, parse_port("65535", &port));
    TEST_ASSERT_EQUAL_UINT(65535, port);
}

static void test_null_arguments(void)
{
    unsigned int port = 80;
    TEST_ASSERT_EQUAL_INT(PORT_INVALID_ARGUMENT, parse_port(NULL, &port));
    TEST_ASSERT_EQUAL_INT(PORT_INVALID_ARGUMENT, parse_port("80", NULL));
    TEST_ASSERT_EQUAL_UINT(80, port);
}

static void test_invalid_syntax(void)
{
    const char *inputs[] = {"", " 80", "80 ", "+80", "-1", "80x"};
    unsigned int port = 80;
    for (size_t i = 0; i < sizeof inputs / sizeof inputs[0]; ++i) {
        TEST_ASSERT_EQUAL_INT_MESSAGE(PORT_INVALID_SYNTAX, parse_port(inputs[i], &port), inputs[i]);
        TEST_ASSERT_EQUAL_UINT(80, port);
    }
}

static void test_out_of_range(void)
{
    unsigned int port = 80;
    TEST_ASSERT_EQUAL_INT(PORT_OUT_OF_RANGE, parse_port("0", &port));
    TEST_ASSERT_EQUAL_UINT(80, port);
    TEST_ASSERT_EQUAL_INT(PORT_OUT_OF_RANGE, parse_port("65536", &port));
    TEST_ASSERT_EQUAL_UINT(80, port);
}

static void test_conversion_overflow(void)
{
    char digits[sizeof(long) * CHAR_BIT + 1];
    memset(digits, '9', sizeof digits - 1);
    digits[sizeof digits - 1] = '\0';

    unsigned int port = 80;
    TEST_ASSERT_EQUAL_INT(PORT_OUT_OF_RANGE, parse_port(digits, &port));
    TEST_ASSERT_EQUAL_UINT(80, port);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_decimal_port);
    RUN_TEST(test_port_bounds);
    RUN_TEST(test_null_arguments);
    RUN_TEST(test_invalid_syntax);
    RUN_TEST(test_out_of_range);
    RUN_TEST(test_conversion_overflow);
    return UNITY_END();
}
