#include "port.h"

#include <errno.h>
#include <stdlib.h>
#include <string.h>

enum port_status parse_port(const char *text, unsigned int *out)
{
    if (text == NULL || out == NULL) {
        return PORT_INVALID_ARGUMENT;
    }

    const size_t digits = strspn(text, "0123456789");
    if (digits == 0 || text[digits] != '\0') {
        return PORT_INVALID_SYNTAX;
    }

    errno = 0;
    const long value = strtol(text, NULL, 10);
    if (errno == ERANGE || value < 1 || value > 65535L) {
        return PORT_OUT_OF_RANGE;
    }

    *out = (unsigned int)value;
    return PORT_OK;
}
