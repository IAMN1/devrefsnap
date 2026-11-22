# Dockerfile and Docker Compose

[Русский](../../../ru/tools/docker/README.md)

| What do you need? | Where to go |
| --- | --- |
| Look up syntax | **Cheat sheets** — [Dockerfile instructions](dockerfile.md), [compose.yaml fields](compose-file.md), [Compose commands](commands.md) |
| Understand how the files work together | **Guide** — [from building an image to a request through two containers](guide.md) |
| See the complete files or try the exercises | **Lab** — [complete Dockerfile](lab.md#dockerfile), [complete three-service compose.yaml](lab.md#composeyaml), [run and exercises](lab.md#run-the-site) |

## First run

Try the [single-service exercise](first-run.md) if this is your first time running Docker. In the [complete example](lab.md), a gateway routes requests to the catalog and help sites. Each service mounts a named volume and explicitly joins a network.

[An app with PostgreSQL and a GitHub Actions test](../compose-and-github-actions.md) · [Development tools](../README.md)
