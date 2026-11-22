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

In your checkout, open `examples/tools/docker-build-context/`, the directory containing [main.py](../../../../examples/tools/docker-build-context/main.py). Build the image from that directory.

```bash
docker build -f dockers/Dockerfile -t devrefsnap-context:local .
```

| Compose file | `build.context` | `build.dockerfile` |
| --- | --- | --- |
| [At the root](../../../../examples/tools/docker-build-context/compose.yaml) | `.` | `dockers/Dockerfile` |
| [In dockers/](../../../../examples/tools/docker-build-context/dockers/compose.yaml) | `..` | `dockers/Dockerfile` |

Use one of these Compose files per run. With a single file and default project settings, Compose resolves `context` from the file’s directory and `dockerfile` from the context. In both layouts, `COPY main.py .` reads the file from the project root.

### Where to put .dockerignore

Place [`.dockerignore`](../../../../examples/tools/docker-build-context/.dockerignore) next to `main.py`, at the build context root. Each line excludes one name at that root.

```text
.venv
.git
.env
```

[Directory tree, full files and run commands for both layouts](build-context.md) · [How Docker reads .dockerignore](https://docs.docker.com/build/concepts/context/#dockerignore-files).

To select a named stage, add `target` under `build`. [Two-stage example](../../../../examples/tools/api-contract-lab/compose.yaml) · [Compose build paths](https://docs.docker.com/reference/compose-file/build/).

## Pass settings

| Who needs the value? | Where to set it | Example |
| --- | --- | --- |
| Compose while reading YAML | The shell or a `.env` in the current working directory. Use `--env-file` to select another file | `${SITE_PORT:-18083}` selects 18083 when the value is empty or missing. A shell value takes precedence in this example. |
| A process inside the container | Service `environment` | `environment: {LOG_LEVEL: info}` passes `LOG_LEVEL=info` to the program |
| A process that takes settings from a file | Service `env_file` | `env_file: ./app.env` supplies `KEY=value` pairs. On a name collision, `environment` takes precedence. |

From the repository root, run `SITE_PORT=18084 docker compose -f examples/tools/compose-site/compose.yaml config`. Under `services.gateway.ports`, the `published` field is `18084`. [Compose file for this example](../../../../examples/tools/compose-site/compose.yaml). The output can contain passwords. Use `-q` to validate without printing values. [YAML interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Container environment](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Connect a database

On a shared network, an app addresses PostgreSQL by its service name, such as `postgres:5432`. This connection needs no published database port. Short-form `depends_on: [postgres]` sets startup order. If the app requires a ready database, set `depends_on.postgres.condition: service_healthy` and define a database `healthcheck`. The app handles later reconnections. [Complete PostgreSQL example](../../../../examples/tools/compose-and-github-actions/compose.yaml) · [Dependency readiness](https://docs.docker.com/compose/how-tos/startup-order/).

## Choose storage

| Task | Entry in the service's `volumes` list | Result |
| --- | --- | --- |
| Keep files when replacing a container | `catalog-pages:/site/catalog` | The named volume keeps the data. Normal `down` retains it. |
| Use a configuration file from the host | `./gateway.conf:/etc/nginx/conf.d/default.conf:ro` | The container reads the host file. The `ro` suffix prevents writes through the mount. |

Mounting a volume makes its contents visible at that path in place of the image files. By default Docker seeds an empty volume with the initial image files. Running `docker compose down -v` deletes project-managed volumes and their data. Volumes marked `external: true` are retained. [Docker volumes](https://docs.docker.com/engine/storage/volumes/) · [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/).

[All Docker materials](README.md)
