<a id="настроить-cors-и-время-обработки"></a>
# Configure CORS and processing time

[Русский](../../../../ru/python/web/fastapi/middleware.md)

Use this page to allow browser access from a specific origin and add a diagnostic header.
The example implements no authentication and does not measure transmission of the complete streaming body.

| Task | Technique | Example |
| --- | --- | --- |
| Allow a specific origin | `CORSMiddleware` with an explicit list | [Complete middleware_app.py](#middleware-and-cors) |
| Add processing duration | HTTP middleware and `perf_counter` | [Complete application](#middleware-and-cors) |
| Check preflight | OPTIONS with browser headers | [Complete tests](testing-lab.md#files-and-middleware) |

[HTTP cards](recipes.md) · [FastAPI reference](README.md) · [Checks](testing.md)

Intermediate level.
Use Python 3.14.
In a separate environment, run `python -m pip install 'fastapi==0.162.0' 'uvicorn[standard]'`.

<a id="middleware-и-cors"></a>
## Middleware and CORS

Save the standalone example in `middleware_app.py`.

[`middleware_app.py`](../../../../../examples/python/web/fastapi/middleware_app.py)

Run `uvicorn middleware_app:app --reload`.
`curl -i -H 'Origin: http://localhost:3000' http://127.0.0.1:8000/` shows `Access-Control-Allow-Origin` and `X-Process-Time`.
For a preflight check, send `OPTIONS` with `Origin` and `Access-Control-Request-Method: GET` headers.
An [automated test](testing.md#files-and-middleware) checks this scenario.

An origin includes scheme, host, and port.
`127.0.0.1` differs from `localhost`.
With credentials, list allowed origins explicitly.
CORS controls browser access to the response.
CORS does not authenticate requests.
The timer measures the path up to obtaining the response object.
The timer does not measure transmission of the complete streaming body.
An unhandled exception may take a different error-handling path.

Sources include [middleware](https://fastapi.tiangolo.com/tutorial/middleware/) and [CORS](https://fastapi.tiangolo.com/tutorial/cors/).
