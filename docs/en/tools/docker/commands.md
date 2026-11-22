# Docker Compose command cheat sheet

[Русский](../../../ru/tools/docker/commands.md)

Run commands in the directory containing `compose.yaml`. The names `gateway` and `catalog` come from the [three-service example](lab.md). Use `docker compose config --services` to see the names in your project.

| Task | Command | Effect |
| --- | --- | --- |
| Validate the file | `docker compose config -q` | Returns exit code 0 for a valid configuration. Omit `-q` to see the resolved settings. |
| Build an image | `docker compose build catalog` | Builds the image. A running container continues using its previous image. |
| Start the project in the background | `docker compose up -d` | Creates missing resources and starts services. Without `-d`, logs stream to the terminal and `Ctrl+C` stops the containers. |
| Build and start | `docker compose up -d --build` | Builds images and recreates containers as needed. |
| Find a stopped container | `docker compose ps -a` | Shows the status of each container, including those that exited. |
| Find the host address | `docker compose port gateway 80` | Prints `127.0.0.1:18083` with the example's default settings. |
| Follow the process log | `docker compose logs --tail 20 -f catalog` | Shows the last 20 lines and new entries. Press `Ctrl+C` to leave the log view. |
| Stop and resume | `docker compose stop catalog`, then `docker compose start catalog` | Keeps the container and its settings. |
| Restart a process | `docker compose restart catalog` | Restarts the same container with its previous settings. |
| Shut down the project | `docker compose down` | Removes project containers and networks. Named volumes remain. |

To select another file, use `-f` before the subcommand. From the repository root, try `docker compose -f examples/tools/compose-site/compose.yaml config --services`. The `-p` flag sets the project name. Use the same name for startup and cleanup. Parallel instances need distinct host ports. [CLI reference](https://docs.docker.com/reference/cli/docker/compose/).

## Choose exec or run

| Task | Command | Where it runs |
| --- | --- | --- |
| Read a file in a running service | `docker compose exec catalog cat message.txt` | In the existing container. For scripts, add `-T` to disable terminal allocation. |
| Run a one-off command | `docker compose run --rm catalog python --version` | In a new container using the service settings. The container is removed when the command exits. Service ports are unpublished by default. |

## Apply a change

| What changed? | What applies the change? |
| --- | --- |
| A Dockerfile or a file included by `COPY` | `docker compose up -d --build`. If a volume covers the path, the container sees the volume's contents. [How this works](guide.md#what-survives-container-recreation). |
| Compose `ports` or `environment` | `docker compose up -d` recreates the affected container. |
| Contents of a bind-mounted host file | The app sees the new data the next time it reads the file. Restart it if it reads settings only at startup. |
| A registry image under the same tag | `docker compose pull gateway`, then `docker compose up -d`. For a database upgrade, check compatibility with the stored data. |

[Single-service rebuild exercise](first-run.md#apply-a-change) · [How up works](https://docs.docker.com/reference/cli/docker/compose/up/).

## Diagnose a failure

| Symptom | What to check |
| --- | --- |
| Cannot connect to Docker Engine | Look for the `Server` section in `docker version`. Check Docker Desktop or Engine and the selected environment in `docker context show`. |
| Service not found | `docker compose config --services` shows the names in the current file. |
| Host port is occupied | Select a free port with `SITE_PORT` and apply it with `up -d`. Check the address with `docker compose port gateway 80`. |
| Gateway returned 502 or a container exited | Read `docker compose ps -a` and `docker compose logs --tail 30 gateway catalog help`. [Restore the route](lab.md#run-the-site). |
| Catalog returned 404 | `docker compose exec catalog ls` lists the available files. The full example request path is `/catalog/message.txt`. |
| Application cannot find PostgreSQL | Check the service name, shared network, and database readiness. [Database connection](compose-file.md#connect-a-database). |

[All Docker materials](README.md)
