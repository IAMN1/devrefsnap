# Write a compose.yaml for your application

[Русский](../../../ru/tools/docker/compose-file.md)

Describe where each service gets its image and how to run its container. Start with one HTTP server. Then see what changes when an application needs a database.

| Task | Compose fields | Example |
| --- | --- | --- |
| Run code from a Dockerfile | `services`, `build`, `ports` | [Complete single-service file](#define-a-service) |
| Choose a different Dockerfile or stage | `context`, `dockerfile`, `target` | [Build paths](#locate-the-dockerfile) |
| Change a port or process setting | `${…}`, `environment`, `env_file` | [Interpolation and environment](#pass-settings) |
| Connect services over a network | `image`, `depends_on`, `healthcheck` | [Application and PostgreSQL](#connect-a-database) |
| Persist data or use a local file | `volumes` | [Volume and file mount](#choose-storage) |

## Define a service

Place `compose.yaml` alongside the [server Dockerfile](dockerfile.md#build-your-first-image) and `message.txt`. This is the entire file for this project. Use the `docker compose` command and the Compose Specification. The top-level `version` field is obsolete. [Example file](../../../../examples/tools/docker-basics/compose.yaml) · [Specification version](https://docs.docker.com/reference/compose-file/version-and-name/).

```yaml
services:
  web:
    build: .
    ports:
      - "127.0.0.1:${SITE_PORT:-18081}:8000"
```

1. Name the service under `services`. Here you can pass `web` to `docker compose logs web`. Indentation groups the settings for that service.
2. Set `build: .` to build your own image from the adjacent Dockerfile. For an existing image, set `image`, as in the database service's `image: postgres:18.6`.
3. Quote the port mapping in the form `"address:host_port:container_port"`. Here the server listens on `0.0.0.0:8000` inside the container. From the host, send requests to `127.0.0.1:18081`. Binding to `127.0.0.1` publishes the port on the host's loopback interface.

Run `docker compose config --services` in the example directory. Expect the single line `web`. Run `docker compose config` to inspect resolved paths and ports. Follow the [first run](README.md#first-run) to check the HTTP response.

## Locate the Dockerfile

With a single Compose file, a relative `context` starts at the directory containing `compose.yaml`. A relative `dockerfile` starts at the build context. For example, if your sources live in `site/` and your recipe lives in `site/docker/Dockerfile`, use the following service definition.

```yaml
services:
  web:
    build:
      context: ./site
      dockerfile: docker/Dockerfile
```

A `COPY message.txt ./` in that Dockerfile reads `site/message.txt`. If the file is named `Dockerfile` and lives at the context root, the short form `build: ./site` is enough.

If your Dockerfile includes `FROM … AS client`, putting `target: client` under `build` selects that stage as the build result. In the API contract example, the `app` and `client` services build from one file. When you specify both `build` and `image`, the pull/build decision depends on `pull_policy`. [Dockerfile with named stages](../../../../examples/tools/api-contract-lab/Dockerfile) · [Services with build.target](../../../../examples/tools/api-contract-lab/compose.yaml) · [Compose build rules](https://docs.docker.com/reference/compose-file/build/).

## Pass settings

Run this command in the `docker-basics` directory to see which port the service would use with the supplied value.

```bash
SITE_PORT=18082 docker compose config
```

Look for `published: "18082"` and `target: 8000`. Compose substitutes `SITE_PORT` while reading the YAML. The expression `${SITE_PORT:-18081}` selects `18081` if the variable is unset or empty. To keep the choice across commands, put `SITE_PORT=18082` in a `.env` next to `compose.yaml`. A shell value takes precedence in this example.

| Consumer | Where to set a value | Result |
| --- | --- | --- |
| Compose when reading YAML | Shell or `.env` | The value is substituted into `ports`. To pass a value to the process, declare it in the service configuration. |
| Program inside the container | `environment: {LOG_LEVEL: info}` on the service | The process sees `LOG_LEVEL=info` if it reads that variable. |
| Program that needs variables from a file | `env_file: ./app.env` on the service | Compose passes the file's `KEY=value` entries to the container. Values in `environment` take precedence. |

After changing settings, run `docker compose up -d`. If the port changed, check it with `docker compose port web 8000`. The output of `config` may contain resolved passwords. Use `config -q` for validation without printing values. [Interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Container environment](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Connect a database

In a separate project, the application `app` connects to the `postgres` service. This excerpt shows connection and readiness settings. To run it, use the [complete compose.yaml](../../../../examples/tools/compose-and-github-actions/compose.yaml), which also sets practice credentials, a volume, and the HTTP health check. [Setup and run](../compose-and-github-actions.md#run-the-application-locally).

```yaml
services:
  app:
    build: .
    environment:
      PGHOST: postgres
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:18.6
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "lab", "-d", "compose_lab"]
      interval: 3s
      timeout: 2s
      retries: 10
```

Compose attaches both services to the project network. The application resolves the name `postgres` and connects to port `5432` on that network. This connection needs no published database port. In the health check, `127.0.0.1` refers to the PostgreSQL container. Inside `app`, the same address points back to the application container.

The short form `depends_on: [postgres]` sets startup order. With `service_healthy`, Compose waits for the database check to pass before starting the app. The app handles any later connection loss. In the complete example, `docker compose up -d --wait` waits for both services to be `healthy`. For a service without a health check, `running` is sufficient. In the complete example, requesting `/health` runs SQL and returns the database name `compose_lab`. [Compose networking](https://docs.docker.com/compose/how-tos/networking/) · [Startup order](https://docs.docker.com/compose/how-tos/startup-order/).

## Choose storage

| What you need | How to mount it | What happens when you recreate the container |
| --- | --- | --- |
| Persist the practice database | Mount `lab-data:/var/lib/postgresql` in the `postgres` service. Declare `lab-data:` under the top-level `volumes:`. | The new project container receives the same named volume. This mount path is for the PostgreSQL 18 image. |
| Read a host file during development | Add `./message.txt:/site/message.txt:ro` to the `web` service's `volumes` list. The file must exist. | The container reads the host file. The mount hides the image copy and `ro` prevents writes through the mount. |

A regular `docker compose down` keeps the named volume. Running `docker compose down -v` removes project-managed volumes, including the practice data in `lab-data`. Use it for an intentional reset. Compose preserves volumes declared with `external: true`. [Compose volumes](https://docs.docker.com/reference/compose-file/volumes/) · [Bind mounts](https://docs.docker.com/engine/storage/bind-mounts/) · [What down removes](https://docs.docker.com/reference/cli/docker/compose/down/).

[Compose commands](commands.md) · [Dockerfile and Docker Compose](README.md)
