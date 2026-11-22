# Choose a Docker Compose command

[Русский](../../../ru/tools/docker/commands.md)

Run these commands in the directory containing `compose.yaml`. The `web` service comes from the [practice project](../../../../examples/tools/docker-basics/compose.yaml). The first run requires a Docker Engine, the Compose plugin, and curl. [Start from the repository root](README.md#first-run).

| What you want to do | Example command | What to expect |
| --- | --- | --- |
| Validate the YAML before starting | `docker compose config -q` | Exit code 0 for a valid configuration. Omit `-q` to see the resolved settings. |
| Build the image separately | `docker compose build web` | A new image or a cached result. A running container keeps using its existing image. |
| Start the application in the background | `docker compose up -d` | Compose creates missing resources and recreates changed containers as needed. |
| Apply changes to files from `COPY` | `docker compose up -d --build web` | Compose builds the image before updating the service. [Try it on one file](#apply-a-change). |
| Find the status and port | `docker compose ps -a` · `docker compose port web 8000` | The first command includes stopped containers. The second prints the running service's published address. |
| Read recent requests | `docker compose logs --tail 20 -f web` | The last 20 lines and new entries as they arrive. Press `Ctrl+C` to leave the log view. |
| Run a command inside a service | `docker compose exec web cat message.txt` | File contents from the running container. [Compare with run](#choose-exec-or-run). |
| Temporarily stop and resume the service | `docker compose stop web`, then `docker compose start web` | The same container with its previous settings. |
| Restart a process with its previous settings | `docker compose restart web` | The service starts again in the same container. |
| Finish working with the project | `docker compose down` | Removes project containers and the project network. By default, named volumes and images are retained. |

Without `-d`, `up` streams logs to the terminal. Pressing `Ctrl+C` there stops the containers. Pressing the same keys during `logs -f` leaves the service running in the background.

Compose uses the directory name as the default project name unless you set one elsewhere. From the repository root, you can select the file explicitly with `docker compose -f examples/tools/docker-basics/compose.yaml config --services`. For a second instance, use `-p` before the subcommand to pick another project name. Use that same name for subsequent commands. The second instance also needs a free host port. [Project and file selection](https://docs.docker.com/reference/cli/docker/compose/).

## Choose exec or run

Start `web` with `docker compose up -d --build`. Then compare these commands from the example directory.

```bash
docker compose exec web cat message.txt
docker compose run --rm web cat message.txt
```

Both print `Hello from Docker!` for the original example. The first reads the file in the running container. Use `exec` to inspect that container's state. In a script, add `-T`, as in `docker compose exec -T web cat message.txt`, to disable terminal allocation.

The second creates a separate container using the `web` configuration, runs `cat`, and removes the container when it exits. Use it for a one-off test. By default `run` skips publishing the service's ports. In a project with dependencies, it can start the services it needs. [exec reference](https://docs.docker.com/reference/cli/docker/compose/exec/) · [run reference](https://docs.docker.com/reference/cli/docker/compose/run/).

## Apply a change

In a separate practice copy, start the original `web` service. Change the line in `message.txt` to `Hello again!`. In the base configuration the Dockerfile copies this file into the image, and Compose starts a container without a host file mount.

```bash
docker compose restart web
docker compose exec web cat message.txt
docker compose up -d --build web
docker compose exec web cat message.txt
```

After `restart`, expect `Hello from Docker!`. After building and recreating the container, expect `Hello again!`. Finish the exercise with `docker compose down`.

| What changed in your project? | What to run | Why |
| --- | --- | --- |
| Dockerfile, source included by `COPY`, or an image dependency | `docker compose up -d --build` | The files must be built into the image |
| `ports` or `environment` in YAML | `docker compose up -d` | Compose creates a container with the new configuration |
| A file available through a bind mount | Inspect the mounted file in the container with `exec` | The change is available through the mount. Restart the process if the app reads the file only at startup. |
| Published image under the same tag | In the [database example](../compose-and-github-actions.md), run `docker compose pull postgres`, then `docker compose up -d` | `pull` downloads the image. `up` applies it. Check image compatibility with the data in the volume. |

[How up works](https://docs.docker.com/reference/cli/docker/compose/up/) · [How restart works](https://docs.docker.com/reference/cli/docker/compose/restart/).

## Diagnose a failure

| Symptom | What to check | What to do next |
| --- | --- | --- |
| Docker cannot connect to the daemon | Does `docker version` include a `Server` section? | Start Docker Engine or Desktop. Check the selected environment with `docker context show`. |
| Compose cannot find the configuration or service | Run `docker compose config --services` in the example directory | Check the YAML path and the service name. This project should list `web`. |
| Port `18081` is occupied during startup | Look for `port is already allocated` or `address already in use` | Run `SITE_PORT=18082 docker compose up -d` with a free port. Request `http://127.0.0.1:18082/message.txt`. |
| The container exited or HTTP does not respond | Run `docker compose ps -a`, then `docker compose logs --tail 30 web` | Check the startup command, listening address, and `docker compose port web 8000`. The `running` state alone does not check HTTP. |
| The server returned HTTP 404 | Run `docker compose exec web ls /site` | Request `/message.txt`. If you changed the image contents, rebuild the service. |
| An app cannot find the database in another container | In the database project, run `docker compose ps -a` and `docker compose logs --tail 30 postgres` | Use the service name and internal port. Check dependency readiness. [Networking and readiness](compose-file.md#connect-a-database). |

For routine cleanup, `down` is usually enough. Its `-v` flag also removes managed named volumes containing data. See [choose storage](compose-file.md#choose-storage) for the effects on the database and host files.

[Docker Compose CLI reference](https://docs.docker.com/reference/cli/docker/compose/) · [Dockerfile and Docker Compose](README.md)
