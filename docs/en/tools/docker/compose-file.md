# compose.yaml field reference

[Русский](../../../ru/tools/docker/compose-file.md)

Define services under `services`. The top-level `volumes` and `networks` sections declare named project resources. To attach a resource, list its name again under the service that uses it. [Complete three-service file](lab.md#composeyaml) · [Guide and request diagram](guide.md).

## Define a service

| What to specify | Service entry | Meaning |
| --- | --- | --- |
| Custom image | `build: .` | Build from the Dockerfile in the directory containing the Compose file |
| Published image | `image: nginx:stable-alpine` | Use the Nginx image with this tag |
| Working directory | `working_dir: /site/catalog` | Start the process in this directory |
| Host port | `ports: ["127.0.0.1:18083:80"]` | Forward requests from local port 18083 to container port 80 |
| Network membership | `networks: [catalog-net]` | Services on this network can find each other by name |
| Storage | `volumes: ["catalog-pages:/site/catalog"]` | Mount the named volume at this container path |

Compose uses the current specification without a top-level `version` field. When a service sets both `build` and `image`, `pull_policy` determines whether Compose pulls or builds. [Compose specification](https://docs.docker.com/reference/compose-file/) · [Build rules](https://docs.docker.com/reference/compose-file/build/).

## Locate the Dockerfile

When `main.py` is at the project root and the Dockerfile is in `dockers/`, use the project root as the build context. Then `COPY main.py .` can find the source file. The tree shows two possible locations for `compose.yaml`. Choose one Compose file per run. The example needs Docker with Compose and the `python:3.14-slim` base image from Docker Hub.

```text
docker-build-context/
├── main.py
├── compose.yaml
└── dockers/
    ├── Dockerfile
    └── compose.yaml
```

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

**Option 1.** [compose.yaml at the root](../../../../examples/tools/docker-build-context/compose.yaml). The dot in `context` selects the directory containing `main.py`.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: dockers/Dockerfile
```

**Option 2.** [compose.yaml in dockers/](../../../../examples/tools/docker-build-context/dockers/compose.yaml). The `..` context goes up one level from the Compose file’s directory to the directory containing `main.py`.

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

To select a named stage, add `target` under `build`. [Two-stage example](../../../../examples/tools/api-contract-lab/compose.yaml) · [Compose build paths](https://docs.docker.com/reference/compose-file/build/).

## Pass settings

| Who needs the value? | Where to set it | Example |
| --- | --- | --- |
| Compose while reading YAML | The shell or a `.env` next to this Compose file | `${SITE_PORT:-18083}` selects 18083 when the value is empty or missing. A shell value takes precedence in this example. |
| A process inside the container | Service `environment` | `environment: {LOG_LEVEL: info}` passes `LOG_LEVEL=info` to the program |
| A process that takes settings from a file | Service `env_file` | `env_file: ./app.env` supplies `KEY=value` pairs. On a name collision, `environment` takes precedence. |

Run `SITE_PORT=18084 docker compose config` to see the resolved port. The output can contain passwords. Use `-q` to validate without printing values. [YAML interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Container environment](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Connect a database

On a shared network, an app addresses PostgreSQL by its service name, such as `postgres:5432`. This connection needs no published database port. Short-form `depends_on: [postgres]` sets startup order. If the app requires a ready database, set `depends_on.postgres.condition: service_healthy` and define a database `healthcheck`. The app handles later reconnections. [Complete PostgreSQL example](../../../../examples/tools/compose-and-github-actions/compose.yaml) · [Dependency readiness](https://docs.docker.com/compose/how-tos/startup-order/).

## Choose storage

| Task | Entry in the service's `volumes` list | Result |
| --- | --- | --- |
| Keep files when replacing a container | `catalog-pages:/site/catalog` | The named volume keeps the data. Normal `down` retains it. |
| Use a configuration file from the host | `./gateway.conf:/etc/nginx/conf.d/default.conf:ro` | The container reads the host file. The `ro` suffix prevents writes through the mount. |

Mounting a volume makes its contents visible at that path in place of the image files. By default Docker seeds an empty volume with the initial image files. Running `docker compose down -v` deletes project-managed volumes and their data. Volumes marked `external: true` are retained. [Docker volumes](https://docs.docker.com/engine/storage/volumes/) · [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).

[All Docker materials](README.md)
