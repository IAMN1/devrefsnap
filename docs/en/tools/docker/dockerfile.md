# Write a Dockerfile and check the image

[Русский](../../../ru/tools/docker/dockerfile.md)

A Dockerfile defines the build steps and the default command for a container. Work through a server that serves one text file. Building it requires a running Docker Engine and the `python:3.14-slim` base image. Docker downloads the image from Docker Hub if necessary.

| Task | Technique | Example |
| --- | --- | --- |
| Write your first file | `FROM`, `WORKDIR`, `COPY`, `USER`, `CMD` | [Minimal server](#build-your-first-image) |
| Choose which files the build can use | Build context and `.dockerignore` | [Copy boundaries](#choose-the-build-context) |
| Speed up an application rebuild | Copy the dependency manifest first | [Package installation](#reuse-the-installation-cache) |
| Choose a command or setting | `RUN`, `CMD`, `ENTRYPOINT`, `ARG`, `ENV` | [Build time and runtime](#choose-an-instruction) |
| Keep build tools in a separate stage | `FROM … AS` and `COPY --from` | [Build stages](#separate-build-and-runtime) |

## Build your first image

From the repository root, change to `examples/tools/docker-basics`. To recreate the example from scratch, start in an empty directory. Put the line `Hello from Docker!` in a file named `message.txt`. Save the following file alongside it with the exact name `Dockerfile`.

```dockerfile
FROM python:3.14-slim

WORKDIR /site
COPY message.txt ./
USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGINT
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
```

| Instruction | What it changes in this example |
| --- | --- |
| `FROM` | Starts with a Python 3.14 runtime. The `3.14-slim` tag can receive updates. Pin the base image by digest when a build needs the same underlying image each time. |
| `WORKDIR` | Creates `/site` if necessary. Relative destinations and the container command use this working directory. |
| `COPY` | Copies a file from the build context to `/site/message.txt`. The image contains a snapshot taken at build time. |
| `USER` | Sets the process UID and GID. The server needs read access and can listen on port `8000`. Writing to a directory would require permission. |
| `EXPOSE` | Documents the internal TCP port. Publish it with `-p` or Compose `ports` to reach it from the host. |
| `STOPSIGNAL` | Selects the stop signal. This Python server handles SIGINT and exits. |
| `CMD` | Sets the default executable and arguments. The JSON array starts Python directly and preserves argument boundaries. |

Build the image from the current directory. Check its contents before setting up networking.

```bash
docker build -t devrefsnap-web:local .
docker run --rm devrefsnap-web:local cat message.txt
```

The `-t` flag names and tags the image. The command `cat message.txt` replaces `CMD` for this run and prints `Hello from Docker!`. The `--rm` flag removes the container when it exits. The image is available for the next run. [Complete Dockerfile](../../../../examples/tools/docker-basics/Dockerfile) · [Start the server with Compose](README.md#first-run).

To check the server directly, publish its port when starting the container. Local port `18081` must be available.

```bash
docker run --rm -p 127.0.0.1:18081:8000 devrefsnap-web:local
```

Open `http://127.0.0.1:18081/message.txt` in your browser. Expect the same line. Press `Ctrl+C` in the server terminal to release the port before running Compose.

If `docker build --help` lists `--check`, run `docker build --check .` in the example directory. BuildKit checks the Dockerfile against its built-in rules. The HTTP request checks the running server. [Build checks](https://docs.docker.com/build/checks/).

## Choose the build context

The final argument to `docker build` sets the **build context**. In `docker build -t devrefsnap-web:local .`, the dot selects the current directory. Source paths in an ordinary `COPY` start at the context root. The `-f` option selects the Dockerfile independently.

For example, run the same build from the **repository root** with the following paths.

```bash
docker build -t devrefsnap-web:local \
  -f examples/tools/docker-basics/Dockerfile examples/tools/docker-basics
```

Place `.dockerignore` at the context root. This application needs only `message.txt`. The first line excludes files from the context and the second restores the required file. Docker still reads the Dockerfile and ignore rules to perform the build. [Complete .dockerignore](../../../../examples/tools/docker-basics/.dockerignore).

```text
*
!message.txt
```

If you add `COPY requirements.txt ./`, also allow `!requirements.txt`. For a `COPY … not found` error, check the last command argument, filename case, and ignore rules. [Build context](https://docs.docker.com/build/concepts/context/).

## Reuse the installation cache

If an app needs packages, copy its manifest before its source code. This excerpt follows `WORKDIR /app` in the PostgreSQL application's Dockerfile. Its build context needs all three files mentioned here. [Complete Dockerfile with Psycopg](../../../../examples/tools/compose-and-github-actions/Dockerfile).

```dockerfile
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py test_app.py ./
```

If only `app.py` changes, Docker can reuse the installation step. Changing `requirements.txt` triggers installation again. The `--no-cache-dir` flag affects pip's own cache. Docker caches build steps separately. [Layer order and the Docker cache](https://docs.docker.com/build/cache/optimize/).

## Choose an instruction

| What you need | Example | When it takes effect |
| --- | --- | --- |
| Install a package in the image | `RUN python -m pip install -r requirements.txt` | At build time unless Docker reuses a cached result |
| Set a replaceable command | `CMD ["python", "app.py"]` | When a container is created without a command override |
| Keep the executable when replacing its arguments | `ENTRYPOINT ["python", "-m", "http.server"]` with `CMD ["8000"]` | With this image, passing `9000` after the image name starts the server on port 9000 |
| Select the base at build time | `ARG PYTHON_VERSION=3.14` before `FROM python:${PYTHON_VERSION}-slim` | Pass a value with `docker build --build-arg PYTHON_VERSION=3.14 .` |
| Set a default process environment variable | `ENV PYTHONUNBUFFERED=1` | The image retains the value. A Compose service can override it with `environment`. |

Exec-form `CMD` and `ENTRYPOINT` do not invoke a shell to expand `$VAR`. Use a BuildKit secret mount for build credentials. Values supplied through `ARG` or `ENV` can appear in the image or build metadata. [Dockerfile instructions](https://docs.docker.com/reference/dockerfile/) · [Build secrets](https://docs.docker.com/build/building/secrets/).

## Separate build and runtime

If producing an artifact needs a compiler or installer, name your build stage with `FROM … AS builder`. Start a fresh stage with another `FROM` and copy the required output into it. This line comes from the final stage of the uv example.

```dockerfile
COPY --from=builder /app/.venv /app/.venv
```

The source path starts at the filesystem root of the `builder` stage. Copying this Python environment requires compatible base images and an identical installation path. When a project needs different final images, each Compose service can select its stage with `build.target`. [Complete uv example](../../python/tooling/uv/automation.md#docker) · [Select a stage in Compose](compose-file.md#locate-the-dockerfile) · [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/).

[Dockerfile and Docker Compose](README.md)
