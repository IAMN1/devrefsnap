# Build a root-level main.py with the Dockerfile in dockers/

[Русский](../../../ru/tools/docker/build-context.md)

When `main.py` is at the project root and the Dockerfile is in `dockers/`, use the project root as the build context. Then `COPY main.py .` can find the source file. The tree shows two possible locations for `compose.yaml`. Choose one Compose file per run. You need a running Docker engine and the `python:3.14-slim` base image. If the image is missing locally, Docker pulls it from Docker Hub on the first build. The `docker compose` commands also require Compose.

```text
docker-build-context/
├── .dockerignore
├── main.py
├── compose.yaml
└── dockers/
    ├── Dockerfile
    └── compose.yaml
```

[main.py](../../../../examples/tools/docker-build-context/main.py) prints its own absolute path so you can see where Docker copied it.

```python
from pathlib import Path

print(Path(__file__).resolve())
```

## Where to put .dockerignore

Place [`.dockerignore`](../../../../examples/tools/docker-build-context/.dockerignore) at the build context root, next to `main.py`. Both Compose layouts use `docker-build-context/` as their context. Exclude the local Python environment, Git data, and settings file.

```text
.venv
.git
.env
```

Each line excludes one name at the context root. The builder can still copy `main.py`. Compose can still read a local `.env` to interpolate variables in its YAML.

If this Dockerfile needs its own rules, use `dockers/Dockerfile.dockerignore`. Docker gives that file precedence over the root ignore list when building with this Dockerfile. [Docker ignore rules](https://docs.docker.com/build/concepts/context/#dockerignore-files).

## Working directory

From the repository root, enter the example directory.

```bash
cd examples/tools/docker-build-context
```

## Build the image

**One Dockerfile for both layouts.** [dockers/Dockerfile](../../../../examples/tools/docker-build-context/dockers/Dockerfile)

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY main.py .
CMD ["python", "main.py"]
```

**Build without Compose.** Run these commands from the example root (`examples/tools/docker-build-context/`). The `-f` path locates the Dockerfile from the current shell directory. The final dot selects that directory as the build context.

```bash
docker build -f dockers/Dockerfile -t devrefsnap-context:local .
docker run --rm devrefsnap-context:local
```

In `COPY main.py .`, the source `main.py` is relative to the context root. Selecting only `dockers/` as the context puts the file outside that boundary. The destination dot refers to the working directory inside the image. With `WORKDIR /app`, the [program](../../../../examples/tools/docker-build-context/main.py) prints `/app/main.py`.

## compose.yaml at the root

[compose.yaml at the root](../../../../examples/tools/docker-build-context/compose.yaml). The dot in `context` selects the directory containing `main.py`.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: dockers/Dockerfile
```

## compose.yaml in dockers/

[compose.yaml in dockers/](../../../../examples/tools/docker-build-context/dockers/compose.yaml). The `..` context goes up one level from the Compose file’s directory to the directory containing `main.py`.

```yaml
services:
  app:
    build:
      context: ..
      dockerfile: dockers/Dockerfile
```

In both layouts, Compose resolves `dockerfile` from the chosen context. Both contexts point to the project root, so the path stays `dockers/Dockerfile`. Choose one command below from the example root. The expected application output is `/app/main.py`.

| File location | Build and run once |
| --- | --- |
| `compose.yaml` | `docker compose -f compose.yaml run --rm --build app` |
| `dockers/compose.yaml` | `docker compose -f dockers/compose.yaml run --rm --build app` |

[Compose file reference](compose-file.md) · [Dockerfile instructions](dockerfile.md)
