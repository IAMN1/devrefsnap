# Dockerfile cheat sheet

[Русский](../../../ru/tools/docker/dockerfile.md)

A Dockerfile describes what goes into an image and which program a container runs by default. [Complete site Dockerfile](lab.md#dockerfile) · [How it fits with Compose](guide.md).

## Build your first image

| Task | Example instruction | Result |
| --- | --- | --- |
| Choose the runtime | `FROM python:3.14-slim` | Python is already installed in the base image. |
| Set the working directory | `WORKDIR /site` | Docker creates the directory if needed. Relative destinations start there. |
| Include files | `COPY --chown=10001:10001 pages/ ./` | Files from `pages/` appear under `/site`. The copies belong to user ID 10001. |
| Run without root privileges | `USER 10001:10001` | The process uses the given user and group IDs. It needs write permission to change a file. |
| Describe an internal port | `EXPOSE 8000` | Documents the port. Compose `ports` or `docker run -p` controls host access. |
| Set the stop signal | `STOPSIGNAL SIGINT` | The practice Python server handles the signal and exits. |
| Set the startup command | `CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]` | The container starts the server. Each array element is one argument. |

In the directory containing the Dockerfile, `docker build -t site:local .` builds an image tagged `site:local`. Running `docker run --rm site:local python --version` replaces the default command for one run and prints the Python version. With a supporting Buildx version, `docker build --check .` checks the instructions. [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) · [Build checks](https://docs.docker.com/build/checks/).

To serve the image directly, `docker run --rm -p 127.0.0.1:18083:8000 site:local` publishes the server on the host. Its catalog file is available at `http://127.0.0.1:18083/catalog/message.txt`. The port must be free. Press `Ctrl+C` in the server terminal to stop it.

## Choose the build context

In `docker build -f deploy/Dockerfile .`, the `-f` option selects the recipe and the dot sets the **context**, the directory of available source files. Source paths in ordinary `COPY` instructions start at the context root. A `.dockerignore` there excludes unwanted files. For `COPY … not found`, check the context, filename, and ignore rules. [Working .dockerignore](../../../../examples/tools/compose-site/.dockerignore) · [Build context](https://docs.docker.com/build/concepts/context/).

## Reuse the installation cache

Excerpt for a Python project with dependencies. Copy the manifest, install packages, then copy the code.

```dockerfile
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY app.py test_app.py ./
```

If only `app.py` changes, Docker can reuse the installation layer. Changing `requirements.txt` triggers installation again. The `--no-cache-dir` option controls pip's own cache. [Complete Dockerfile with dependencies](../../../../examples/tools/compose-and-github-actions/Dockerfile) · [Docker build cache](https://docs.docker.com/build/cache/optimize/).

## Choose an instruction

| When you need the value or action | What to use |
| --- | --- |
| Run a command at build time | `RUN`, for example to install packages |
| Replace the entire command at startup | `CMD ["python", "app.py"]` |
| Fix the program and replace its arguments | `ENTRYPOINT ["python", "-m", "http.server"]` with `CMD ["8000"]`. Pass `9000` after the image name to change the port. |
| Supply a build parameter | `ARG PYTHON_VERSION=3.14` before `FROM python:${PYTHON_VERSION}-slim`. Set the value with `docker build --build-arg PYTHON_VERSION=3.14 .`. |
| Set a runtime environment default | `ENV PYTHONUNBUFFERED=1`. A service can override it with `environment`. |

To reuse the exact same base image across builds, pin the image by digest. Tags can receive updates.

JSON-array `CMD` and `ENTRYPOINT` do not invoke a shell to expand `$VAR`. BuildKit provides a separate mechanism for credentials. [Build secrets](https://docs.docker.com/build/building/secrets/).

## Separate build and runtime

If only the build needs a compiler, name the stage with `FROM … AS builder`. In the next stage, use `COPY --from=builder` to transfer the result. A service can select a stage with `build.target`. [Complete uv example and Python environment compatibility](../../python/tooling/uv/automation.md#docker) · [Select a stage in Compose](compose-file.md#locate-the-dockerfile).

[All Docker materials](README.md)
