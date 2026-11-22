# Run one service for the first time

[Русский](../../../ru/tools/docker/first-run.md)

A first exercise with Docker. The server returns a single text file. For the three-service example, open the [lab](lab.md).

## First run

Start Docker Desktop or a Docker Engine with the Compose plugin. Run these commands in Bash or Zsh from the repository root. The first run needs curl 7.71 or later and access to Docker Hub. The example uses local port `18081` by default. Python's HTTP server is for local practice. [Install Compose](https://docs.docker.com/compose/install/) · [Python http.server](https://docs.python.org/3.14/library/http.server.html).

```bash
cd examples/tools/docker-basics
docker version
docker compose version
docker compose config -q
docker compose up --build -d
docker compose ps
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18081/message.txt
```

Look for a `Server` section in `docker version`. A successful `config -q` exits silently. The `up` command builds the image from the [Dockerfile](../../../../examples/tools/docker-basics/Dockerfile) and starts the `web` service defined in [compose.yaml](../../../../examples/tools/docker-basics/compose.yaml). The `-d` flag returns control to your terminal.

In the `ps` output, look for `web` and the mapping `127.0.0.1:18081->8000/tcp`. While the server starts, curl may report a connection error and retry the request. A successful request prints the contents of [message.txt](../../../../examples/tools/docker-basics/message.txt).

```text
Hello from Docker!
```

Read the request in the log. Then remove the practice container and project network. The built image stays on your machine.

```bash
docker compose logs --tail 5 web
docker compose down
```

## Apply a change

In a separate practice copy of the example directory, run `docker compose up -d --build`. Change the line in `message.txt` to `Hello again!`. In the base configuration the Dockerfile copies this file into the image, and Compose starts a container without a host file mount.

```bash
docker compose restart web
docker compose exec web cat message.txt
docker compose up -d --build web
docker compose exec web cat message.txt
```

After `restart`, expect `Hello from Docker!`. After building and recreating the container, expect `Hello again!`. Finish the exercise with `docker compose down`.

[All Docker materials](README.md)
