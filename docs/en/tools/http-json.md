# Read an HTTP response with JSON

[Русский](../../ru/tools/http-json.md) · [Development tools](README.md)

Send a GET request from a terminal and inspect the server response. The practice server runs on your computer and returns JSON from a file.

| Task | Technique | Example |
| --- | --- | --- |
| See the response status, headers, and body | `curl -i` | [HTTP response](#inspect-the-http-response) |
| Read the name from the response body | `jq -r '.name'` | [JSON field](#extract-a-json-field) |

## Start the practice server

You need `python3`, `curl`, and `jq`. The commands use Bash or Zsh. The server uses the Python standard library. The example was tested with Python 3.14.

In the first terminal, run the command from the repository root. The server reads the [complete practice file `item.json`](../../../examples/tools/http-json/item.json) and listens only on the local address `127.0.0.1`.

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory examples/tools/http-json
```

Leave the server running. If port `8765` is in use, choose a free port and replace `8765` in the server and request commands.

## Inspect the HTTP response

Use `curl -i URL` to see the status line, headers, and body of a GET response. Use `curl -I URL` to send a HEAD request, whose response has no body.

For the practice example, [start the local server](#start-the-practice-server), then run this command in the second terminal. The `--noproxy 127.0.0.1` option connects directly to the local server.

```bash
curl --noproxy 127.0.0.1 -i http://127.0.0.1:8765/item.json
```

The abbreviated output looks like this.

```http
HTTP/1.0 200 OK
Content-type: application/json

{"id": 1, "name": "Book"}
```

On the first line, the status code `200` means the request succeeded. The `Content-Type` header indicates the format of the body. The response body starts after the blank line.

If the server returns `404`, check the `/item.json` path in the URL and the directory passed to `--directory`.

## Extract a JSON field

Use `jq -r '.name'` with a successful response whose JSON body contains a `name` field. Pass only the body to `jq`.

For the practice example, [start the local server](#start-the-practice-server) and [check the response status and type](#inspect-the-http-response). Remove `-i` from the request. The `-sS` flags hide the progress meter and keep `curl` error messages visible.

```bash
curl --noproxy 127.0.0.1 -sS http://127.0.0.1:8765/item.json | jq -r '.name'
```

The `.name` filter extracts the value of the `name` field. The `-r` option prints the string without JSON quotes.

```text
Book
```

Press `Ctrl+C` in the first terminal to stop the server.

## Sources

- [curl manual](https://curl.se/docs/manpage.html)
- [jq 1.7 manual](https://jqlang.org/manual/v1.7/)
- [Python 3.14 `http.server` module](https://docs.python.org/3.14/library/http.server.html#command-line-interface)
