# Lab. A three-service site

[Русский](../../../ru/tools/docker/lab.md)

This site has one public entry point on the local machine. The `/catalog/` route opens the catalog and `/help/` opens help. Both final files are shown in full below. The source files are in `examples/tools/compose-site/`. [Dockerfile](../../../../examples/tools/compose-site/Dockerfile) · [compose.yaml](../../../../examples/tools/compose-site/compose.yaml).

| Service | Responsibility | Named volume | Network |
| --- | --- | --- | --- |
| `gateway` | Accept HTTP requests and choose the section | `requests` stores the access log | `catalog-net` and `help-net` |
| `catalog` | Serve the catalog text | `catalog-pages` stores catalog files | `catalog-net` |
| `help` | Serve the help text | `help-pages` stores help files | `help-net` |

## Dockerfile

One [Dockerfile](../../../../examples/tools/compose-site/Dockerfile) defines the image for both content services. Compose selects a different working directory for each service.

```dockerfile
FROM python:3.14-slim
WORKDIR /site
COPY --chown=10001:10001 pages/ ./
USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGINT
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
```

## compose.yaml

The complete [compose.yaml](../../../../examples/tools/compose-site/compose.yaml) uses the published Nginx image for the gateway. Only the gateway needs a host port.

```yaml
services:
  gateway:
    image: nginx:stable-alpine
    ports:
      - "127.0.0.1:${SITE_PORT:-18083}:80"
    volumes:
      - ./gateway.conf:/etc/nginx/conf.d/default.conf:ro
      - requests:/var/log/site
    networks: [catalog-net, help-net]
    depends_on: [catalog, help]

  catalog:
    build: .
    working_dir: /site/catalog
    volumes:
      - catalog-pages:/site/catalog
    networks: [catalog-net]

  help:
    build: .
    working_dir: /site/help
    volumes:
      - help-pages:/site/help
    networks: [help-net]

volumes:
  requests:
  catalog-pages:
  help-pages:

networks:
  catalog-net:
  help-net:
```

The example also includes the [Nginx routes](../../../../examples/tools/compose-site/gateway.conf), [catalog text](../../../../examples/tools/compose-site/pages/catalog/message.txt), and [help text](../../../../examples/tools/compose-site/pages/help/message.txt). The [.dockerignore](../../../../examples/tools/compose-site/.dockerignore) keeps the page directory in the build context.

<details>
<summary>Complete gateway.conf with both routes</summary>

[Source gateway.conf](../../../../examples/tools/compose-site/gateway.conf)

```nginx
server {
    listen 80;
    access_log /var/log/site/requests.log;

    location /catalog/ {
        proxy_pass http://catalog:8000/;
    }

    location /help/ {
        proxy_pass http://help:8000/;
    }
}
```

The trailing slash in `proxy_pass http://catalog:8000/;` replaces the `/catalog/` prefix with `/`. The catalog server therefore receives a request for `/message.txt`. [proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass).

</details>

## Run the site

Start Docker Desktop or Docker Engine with the Compose plugin. You need Linux containers, curl 7.71 or newer, free port `18083`, and access to Docker Hub for the initial image downloads. Use Bash or Zsh. The Python server is for local practice. For the first run, use a project with empty practice volumes.

Run this block from the repository root. Run subsequent commands from the same example directory.

```bash
cd examples/tools/compose-site
docker compose config -q
docker compose up -d --build
docker compose ps
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/catalog/message.txt
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/help/message.txt
```

Expect three running services. The two requests return different lines.

```text
Catalog is ready.
Help is ready.
```

If the port is occupied, run `export SITE_PORT=18084` before startup to select a free port. Use the same port in your requests. If the gateway returns HTTP 502, check `docker compose logs --tail 20 gateway catalog help`. The gateway may briefly return 502 while a backend starts. The curl command retries the request. If you recreate one content container separately and its address changes, run `docker compose restart gateway` so Nginx resolves its name again.

## Exercise 1. Trace a request

Find both requests in the gateway volume.

```bash
docker compose exec gateway tail -n 5 /var/log/site/requests.log
```

Look for status `200` on both routes. Read the `PORTS` column in `docker compose ps`. Only `gateway` has a host address. On the internal paths the gateway uses service names. [Request flow diagram](guide.md).

View the request from the gateway. Inside its container, both pages are reachable by service name and internal port.

```bash
docker compose exec gateway wget -qO- http://catalog:8000/message.txt
docker compose exec gateway wget -qO- http://help:8000/message.txt
```

## Exercise 2. Check persistence after recreation

Change only the practice catalog text. This command overwrites `message.txt` inside the `catalog-pages` volume. The source file in the repository stays intact.

```bash
docker compose exec catalog sh -c 'echo "Catalog updated." > message.txt'
docker compose down
docker compose up -d
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/catalog/message.txt
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/help/message.txt
```

The catalog returns `Catalog updated.` and help returns its original text. Keep the same project name and directory so Compose mounts the same volumes.

## Finish

Run `docker compose down` to remove the containers and networks. The volumes remain available for the next run. For a full reset of this practice project, use `docker compose down -v`. This removes all three named volumes, including the changed page and the access log.

[All Docker materials](README.md)
