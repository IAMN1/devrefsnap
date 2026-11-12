#include "port.h"

#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
    if (argc != 2) {
        fputs("Usage: port-check PORT\n", stderr);
        return EXIT_FAILURE;
    }

    unsigned int port;
    if (parse_port(argv[1], &port) != PORT_OK) {
        fputs("Expected a decimal port from 1 to 65535.\n", stderr);
        return EXIT_FAILURE;
    }

    printf("Port: %u\n", port);
    return EXIT_SUCCESS;
}
