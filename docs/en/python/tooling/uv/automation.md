<a id="ci-docker-кэш-и-диагностика-uv"></a>
# uv in CI and Docker, caching, and diagnostics

[Русский](../../../../ru/python/tooling/uv/automation.md)

Use this page to check a project with `uv.lock` in CI or build it in a container.
Use diagnostics when installation or dependency resolution fails.

| Task | Technique | Example / details |
| --- | --- | --- |
| Reproduce checks in CI | Pin uv and Python and use `--locked` | [GitHub Actions](#github-actions) |
| Build the application environment | Separate builder and runtime | [Docker](#docker) |
| Check the lockfile before committing | `uv lock --check` | [Pre-commit](#check-the-lockfile-in-pre-commit) |
| Diagnose installation failures | Cache, `uv tree`, and TLS checks | [Diagnostics](#diagnostics) |

Advanced level.
Requires a working project with `pyproject.toml`, `uv.lock`, and tests.
[uv reference](README.md).


## GitHub Actions

The following snippet contains steps within a job on a suitable runner.
Check the Actions refs separately.
Pin Actions refs according to project policy.
The major-version refs shown are examples.

```yaml
steps:
  - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
  - uses: astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0
    with:
      version: "0.12.13"
      python-version: "3.14"
      enable-cache: true
  - run: uv sync --locked
  - run: uv run --locked pytest
  - run: uv run --locked ruff check .
  - run: uv format --check
```

Declare pytest and Ruff in the project's dev group.
`uv format` uses its own mechanism to run Ruff.
To use the single formatter version pinned in the lockfile, run `uv run --locked ruff format --check .`.
Check the runner's Python version and platform separately from the lockfile.
Test supported combinations with a matrix.


## Docker

The complete example is for a simple non-packaged application with `main.py` at the root.
Prepare the project files before building.
Both Python images in the Dockerfile must have compatible paths, operating systems, and architectures.
For reproducible production builds, pin image digests as well.

```dockerfile
FROM ghcr.io/astral-sh/uv:0.12.13 AS uv
FROM python:3.14-slim AS builder
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
COPY main.py ./

FROM python:3.14-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/main.py ./main.py
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "main.py"]
```

For a package with `src/`, install dependencies first with `--no-install-project`.
Then copy the code.
Install the project with `uv sync --locked --no-dev --no-editable`.
The project still requires installation if you copy a virtual environment created before it was installed.
The application also needs a non-root policy, writable paths, and signal handling.
Keep the local `.venv` out of the Linux image.
Add `.venv` to `.dockerignore`.

<a id="проверка-lock-в-pre-commit"></a>
## Check the lockfile in pre-commit

The following is a `.pre-commit-config.yaml` fragment.
Install pre-commit separately.
Make uv available on PATH.
The snippet runs a local check without automatically rewriting the lockfile.

```yaml
repos:
  - repo: local
    hooks:
      - id: uv-lock-check
        name: check uv.lock
        entry: uv lock --check
        language: system
        pass_filenames: false
        files: ^(pyproject\.toml|uv\.lock)$
```

The official [uv-pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/) integration also provides hooks for generating lockfiles and exports.
Use hook IDs and a `rev` available in the selected repository version.

<a id="кэш-и-параллелизм"></a>
## Cache and parallelism

Use `uv cache dir`, `uv cache size`, and `uv cache prune` for individual operations.
`uv cache clean` deletes the cache.
The command can slow down the next run.
Avoid clearing the cache as a routine optimization.
`--no-cache` bypasses the cache and helps diagnose its impact. Speed still depends on the workload.

The following is a job environment fragment.
Adapt the paths.
Grant access only to the necessary users.

```bash
export UV_CACHE_DIR=/path/to/job/cache
export UV_CONCURRENT_DOWNLOADS=8
export UV_CONCURRENT_BUILDS=4
```

Limit parallelism according to the runner and package service resources.
For your own comparisons, record commands, lockfile, Python, platform, network, and whether the cache was cold or warm.
`pip install` and `uv lock` perform different tasks, so comparing them cannot establish an installation speedup.

<a id="диагностика"></a>
## Diagnostics

| Task | Action |
| --- | --- |
| Find why a dependency was selected | `uv tree --reverse` |
| Inspect resolution logs | `uv -v lock`. Review URLs and data in the logs before publishing them |
| Upgrade a specific candidate | `uv lock --upgrade-package NAME`. Incompatible constraints still apply |
| Check environment dependencies | `uv pip check` |
| Check known vulnerabilities | `uv audit`. Network access is required, and results depend on advisory sources |
| Use a corporate index | `UV_DEFAULT_INDEX` or the index setting. Keep credentials out of commits |
| Diagnose TLS failure | Check the server name, time, and CA chain. If needed, use `--system-certs` or `SSL_CERT_FILE` according to the documentation |

`UV_INDEX_URL` is the old setting name.
For uv 0.12.13, use `UV_DEFAULT_INDEX`.
Avoid using `UV_SSL_VERIFY=0` and `UV_LOG_LEVEL` to configure uv 0.12.13.
Keep TLS verification enabled when troubleshooting installation.
Disabling verification changes which package code you trust.

<a id="источники"></a>
## Sources

[CI](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/),
[pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/), [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/),
[environment variables](https://docs.astral.sh/uv/reference/environment/).
