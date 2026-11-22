<a id="запустить-api-и-собрать-контейнер"></a>
# Run an API and build a container

[Русский](../../../../ru/python/web/fastapi/deployment.md)

Use this page to run the practice API, choose processes, or build a local container.
`minimal.py` must be importable from the launch directory.

| Task | Technique | Example / details |
| --- | --- | --- |
| Restart the server when code changes | Uvicorn `--reload` | [Development](#development-and-multiple-processes) |
| Run multiple processes | `--workers` with separate process memory | [Workers](#development-and-multiple-processes) |
| Use an existing Gunicorn deployment | Separate `uvicorn-worker` | [Startup option](#gunicorn-as-a-separate-option) |
| Build a container or save the schema | Dockerfile or `app.openapi()` | [Container](#container-for-the-minimal-application) · [OpenAPI](#save-openapi) |

[Quick reference](README.md) · [First application](README.md#first-run)

| Parameter | Value |
| --- | --- |
| Level | Intermediate for startup, advanced for processes and containers |
| Prerequisites | Virtual environment and terminal. The container requires Docker |

Run all commands in a separate practice directory with `minimal.py` from this topic's README.
The example demonstrates local startup without publishing the service.

<a id="разработка-и-несколько-процессов"></a>
## Development and multiple processes

Use Python 3.14, FastAPI 0.165.0, and Uvicorn 0.54.0.
Run `python -m pip install 'fastapi==0.165.0' 'uvicorn[standard]==0.54.0'`.

```bash
uvicorn minimal:app --reload --host 127.0.0.1 --port 8000
```

In another terminal, run `curl http://127.0.0.1:8000/`.
Expect `200` and `{"message":"Привет"}`.
`Ctrl+C` stops the server.
`--reload` restarts the server when files change.
Use this mode in development.

Run multiple processes with reload disabled.

```bash
uvicorn minimal:app --host 127.0.0.1 --port 8000 --workers 2
```

This example uses two workers.
Choose the worker count for the server's workload.
Each process has its own memory.
Each process runs its own lifespan.
The item dictionary in `main.py` therefore cannot serve as a shared database.
For external access behind a proxy or within a container, specify `--host 0.0.0.0`.
Configure HTTPS for the environment.
Configure proxy-header trust for the environment.
`--reload` and `--workers` are mutually exclusive.

<a id="gunicorn-как-отдельный-вариант"></a>
## Gunicorn as a separate option

If the Linux/Unix deployment already uses Gunicorn, install `gunicorn` and the separate `uvicorn-worker` in the application environment.

```bash
python -m pip install gunicorn uvicorn-worker
gunicorn minimal:app -w 2 -k uvicorn_worker.UvicornWorker -b 127.0.0.1:8000
```

The old `uvicorn.workers.UvicornWorker` path is deprecated.
For a simple run, Uvicorn's built-in workers are sufficient.
Gunicorn is optional for this example.
See [Uvicorn deployment](https://uvicorn.dev/deployment/).

<a id="контейнер-для-минимального-приложения"></a>
## Container for the minimal application

Create `requirements.txt` in the practice directory.
This file contains the minimum dependencies for `minimal.py`.
The other recipes can require additional packages.

```text
fastapi==0.165.0
uvicorn==0.54.0
```

Use the following Dockerfile.

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY minimal.py .
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "minimal:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fastapi-training .
docker run --rm -p 127.0.0.1:8000:8000 fastapi-training
```

The commands build a local image.
They then start a container with a port available only on localhost.
Check the response with `curl http://127.0.0.1:8000/`.
Stop the container with `Ctrl+C`.
`--rm` removes the exited container.
The image remains available locally.
The example does not publish to a registry.

Update the base image tag and package versions deliberately.
This Dockerfile does not verify support across all platforms and architectures.
For a reproducible project environment, pin transitive dependencies with a lockfile.
Pin the image digest if needed.
Orchestrators often run one process per container.
They then scale the containers.
The choice depends on the infrastructure.

<a id="сохранить-openapi"></a>
## Save OpenAPI

The command imports the practice application.
Then it writes or overwrites `openapi.json` in the current directory.

```bash
python -c 'import json; from minimal import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))' > openapi.json
```

You can also retrieve `/openapi.json` from the running server.
Schema generation sends no requests to routes.
Use [behavioral tests](testing.md) to check route behavior separately.

<a id="источники"></a>
## Sources

- [FastAPI server startup](https://fastapi.tiangolo.com/deployment/manually/), [workers](https://fastapi.tiangolo.com/deployment/server-workers/).
- [FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/), [HTTPS](https://fastapi.tiangolo.com/deployment/https/).
- [Uvicorn deployment](https://uvicorn.dev/deployment/), [settings](https://uvicorn.dev/settings/).
