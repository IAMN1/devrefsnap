#ifndef PORT_PARSER_PORT_H
#define PORT_PARSER_PORT_H

enum port_status {
    PORT_OK,
    PORT_INVALID_ARGUMENT,
    PORT_INVALID_SYNTAX,
    PORT_OUT_OF_RANGE,
};

/* Accept a nonempty decimal string in the range 1..65535.
 * Both pointers are borrowed. Write to out only on PORT_OK.
 */
enum port_status parse_port(const char *text, unsigned int *out);

#endif
