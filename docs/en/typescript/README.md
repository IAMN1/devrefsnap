# TypeScript

[Catalog](../README.md) · [Русский](../../ru/typescript/README.md)

Send `GET /` to a local API from Node.js. Use TypeScript to check types in your code, then validate the server's data at runtime.

| Task | Technique |
| --- | --- |
| Check types before starting an API | [`tsc --noEmit`](#check-types-without-a-server) |
| Validate data from the network | [`response.ok`, `unknown`, and a property check](#read-and-validate-a-json-response) |
| Send a request and see the response | [Run the server and client](#run-the-client) |

## Check types without a server

From the repository root, check the [client](../../../examples/typescript/http-client/client.mts) with Node.js 26 and npm. On the first run, npm downloads TypeScript 6.0.3 if the package is missing from its cache.

```bash
npm exec --yes --package=typescript@6.0.3 -- tsc \
  --ignoreConfig --strict --noEmit --target ES2022 --module NodeNext \
  --lib ES2022,DOM examples/typescript/http-client/client.mts
```

The compiler exits silently with status 0 on success. To see a type error in a practice copy, replace `return { message: data.message }` with `return { message: 42 }`. Repeat the command. The compiler reports that a `number` cannot be assigned to a `string` property. Restore the original line before running the client.

## Read and validate a JSON response

The client expects an object with a string `message` property. The `Greeting` type describes the value you get from `await getGreeting(url)`.

```typescript
type Greeting = { message: string };
```

Excerpt from `getGreeting`. The `url` parameter holds the API address.

```typescript
const response = await fetch(url);
if (!response.ok) {
  throw new Error(`HTTP ${response.status}`);
}
const data: unknown = await response.json();
if (
  typeof data !== "object" ||
  data === null ||
  !("message" in data) ||
  typeof data.message !== "string"
) {
  throw new Error("Expected a JSON object with a string message");
}
```

`response.ok` is `true` for statuses from 200 to 299. Check the status before reading the JSON. `response.json()` parses the response body. The `unknown` type requires you to narrow the value before accessing its properties. After the `if` block, the compiler knows that `data.message` is a string.

## Run the client

Use Node.js 26 with npm and Python 3.14. The compile command uses TypeScript 6.0.3 from the npm cache. If the package is missing from the cache, npm downloads it. The client uses the built-in `fetch` in Node.js.

In the first terminal, start the [minimal FastAPI server](../../../examples/python/web/fastapi/minimal.py) from the repository root. Port `8000` must be free.

```bash
api_env=$(mktemp -d)
python3.14 -m venv "$api_env"
"$api_env/bin/python" -m pip install 'fastapi==0.162.0' 'uvicorn==0.54.0'
"$api_env/bin/python" -m uvicorn minimal:app --app-dir examples/python/web/fastapi --host 127.0.0.1 --port 8000
```

In the second terminal, compile the [complete client `client.mts`](../../../examples/typescript/http-client/client.mts) from the repository root. Run the resulting `client.mjs` file.

```bash
cd examples/typescript/http-client
client_dir=$(mktemp -d)
npm exec --yes --package=typescript@6.0.3 -- tsc \
  --ignoreConfig --strict --noEmitOnError --target ES2022 --module NodeNext \
  --lib ES2022,DOM --outDir "$client_dir" client.mts
node "$client_dir/client.mjs"
```

`--ignoreConfig` lets you compile the specified file independently of `tsconfig.json`. `--strict` enables strict type checking. `--noEmitOnError` prevents JavaScript output if compilation reports an error. The `DOM` type library supplies declarations for `fetch` and `Response`. The `.mjs` extension marks a JavaScript module and allows top-level `await`.

On success, the client prints `Привет`. For a `404` response, the client exits with `HTTP 404`. If a successful JSON response contains a numeric `message`, the client exits with `Expected a JSON object with a string message`.

Stop the server with `Ctrl+C` in the first terminal. The paths `$api_env` and `$client_dir` point to the temporary directories.

In the [end-to-end lab](../tools/api-contract-lab.md), a client checks two FastAPI responses backed by PostgreSQL locally and in CI.

## Sources

- [TypeScript Handbook on narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).
- [`tsc` options](https://www.typescriptlang.org/docs/handbook/compiler-options.html), [TypeScript 6.0 on `--ignoreConfig`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html#specifying-command-line-files-when-tsconfigjson-exists-is-now-an-error), and [TypeScript 4.7 on `.mts` and `.mjs`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-7.html#new-file-extensions).
- [Node.js 26.8.2 on `fetch`](https://nodejs.org/download/release/v26.8.2/docs/api/globals.html#fetch), [Fetch Standard on `Response.ok`](https://fetch.spec.whatwg.org/#dom-response-ok), and [`npm exec` documentation](https://docs.npmjs.com/cli/v11/commands/npm-exec/).
