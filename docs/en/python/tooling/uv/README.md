
# uv

[Русский](../../../../ru/python/tooling/uv/README.md)

Use uv to manage a Python project's interpreter, environment, dependencies, and lockfile.
Speed improvements depend on the project, network, and cache.
The material makes no universal numerical claims.

<a id="быстрый-поиск"></a>
## Quick lookup

Run individual commands in your project.
Installing and updating dependencies changes the environment and lockfile.

| Task | Command | Details |
| --- | --- | --- |
| Create an application | `uv init my-project` | [Project](projects.md) |
| Add a dependency | `uv add requests` | [Dependencies](projects.md#add-upgrade-and-remove-dependencies) |
| Add development tools | `uv add --dev pytest ruff` | [Groups](projects.md#groups-and-platforms) |
| Synchronize | `uv sync --locked` | [Lockfile](projects.md#lockfile-and-environment) |
| Run a command | `uv run --locked python main.py` | [Project](projects.md) |
| Upgrade a package | `uv lock --upgrade-package requests` | [Updates](projects.md#add-upgrade-and-remove-dependencies) |
| Export with hashes | `uv export --locked -o requirements.txt` | [Export](projects.md#export-and-the-pip-interface) |
| Check types | `uv check` uses ty | [Checks](#set-up-the-environment-and-checks) |
| Format | `uv format` uses Ruff | [Checks](#set-up-the-environment-and-checks) |
| Check known vulnerabilities | `uv audit` requires network access | [Diagnostics](automation.md#diagnostics) |

| Parameter | Value |
| --- | --- |
| Command version | uv 0.12.13 |
| Prerequisites | Installed uv and Python for the offline practice example |

<a id="навигация"></a>

<a id="базовый-уровень"></a>

<a id="начать-проект"></a>
## Start a project

**Situation** — create a new application and run Python from its environment.
**Change** — run the snippet in a directory where `my-project` does not exist yet.

```bash
uv init my-project
cd my-project
uv sync
uv run python -c 'import sys; print(sys.prefix)'
```

**Result** — uv creates the project, lockfile, and `.venv` environment. The command prints the environment path.
The commands may download Python and dependencies.
The [complete offline scenario](projects.md#offline-practice-project) uses an already installed Python.


Choose an installation method from the [Astral instructions](https://docs.astral.sh/uv/getting-started/installation/).
Options include a standalone installer, a supported package manager, or `python -m pip install uv` in a suitable environment.
The installer executes downloaded code.
Read the instructions and inspect the source first.
Check `uv --version`.
Check `uv help`.
Specific features depend on the version.

`uv run` manages the project environment without manual activation.
Use `uv venv` for a separate environment.
For activation in Bash or Zsh, use `source .venv/bin/activate`.
In PowerShell, use `.venv\Scripts\Activate.ps1`.
In cmd.exe, use `.venv\Scripts\activate.bat`.
Use the commands for your shell.

The [complete offline recipe](projects.md#offline-practice-project) downloads neither Python nor packages.

<a id="средний-уровень"></a>

<a id="уточнить-окружение-и-проверки"></a>
## Set up the environment and checks

**Situation** — add pytest to a project and record the dependency in the declaration and lockfile.
**Change** — add pytest to the dev group so the project tracks it.
Use the snippet in an existing uv project.

```bash
uv add --dev pytest
uv run --locked python -m pytest
```

**Result** — pytest belongs to the dev group, and tests run in the project environment.
Adding the package requires an accessible index or cache.
The test files must already exist.
[Groups and platforms](projects.md#groups-and-platforms).


`uv python list` shows discovered and available versions.
`uv python install 3.14` downloads Python.
`uv python pin 3.14` writes a version request to `.python-version`. It leaves the default system path alone.
`project.requires-python` in `pyproject.toml` defines the project's supported Python versions.

In uv 0.12.13, `uv check` runs type checking through ty.
`uv format` runs Ruff formatting.
These commands do not run general-purpose lint checks or sort imports.
For linting and import sorting, add Ruff as a development dependency.
Use `uv run ruff check .` or `uv run ruff check --select I --fix .`.
The fix command modifies files.
Review the diff after applying fixes.
`uv run pytest -n auto` requires `pytest-xdist` to be installed.
Tests are covered in [pytest](../../testing/pytest/README.md).

<a id="продвинутый-уровень"></a>

<a id="повторять-сборки-и-диагностировать-проблемы"></a>
## Reproduce builds and diagnose problems

**Situation** — CI must fail if `pyproject.toml` diverges from the saved lockfile.
**Change** — use `--locked` when synchronizing and running commands.
Use the snippet for a project with pytest as a development dependency.

```bash
uv sync --locked
uv run --locked pytest
```

**Result** — an inconsistent lockfile causes failure. A consistent lockfile supplies the selected package versions.
`--frozen` skips the declaration consistency check required by this CI scenario.
[Complete CI configuration](automation.md#github-actions).


Commit `pyproject.toml` and `uv.lock`.
Pin uv and Python in CI.
Production installations often exclude the dev group.
Account for additional default groups separately.

[CI and Docker](automation.md) show the build boundaries.
If you have [cache or TLS](automation.md#diagnostics) problems, diagnose them first.
Keep verification enabled by default.
Workspaces group several Python packages under a shared lockfile.
Their scope is Python packages within the monorepo.

<a id="частые-ошибки"></a>
## Common errors

| Unsuitable command or expectation | Use in uv 0.12.13 |
| --- | --- |
| `uv update`, `uv sort`, `uv info`, `uv outdated`, `uv show` | `lock --upgrade`, Ruff, `uv help`, `uv pip list --outdated`, `uv pip show` |
| `uv sync --parallel` | Operations already use internal parallelism. Configure documented concurrency settings if needed |
| `uv sync --optimize` | If you need bytecode, use `uv sync --compile-bytecode`. This compiles bytecode only |
| `uv cache info` | `uv cache dir`, `uv cache size` |
| A “with hashes” comment on `--no-hashes` | This flag removes hashes |
| Expecting Poetry migration to reuse its lockfile automatically | `uv.lock` uses a separate format. Check migration and the new dependency resolution separately |

<a id="источники"></a>
## Sources

- [uv CLI](https://docs.astral.sh/uv/reference/cli/), [Python versions](https://docs.astral.sh/uv/concepts/python-versions/).
- [Lock and sync](https://docs.astral.sh/uv/concepts/projects/sync/), [dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/).
- [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/), [cache](https://docs.astral.sh/uv/concepts/cache/).

[Python catalog](../../README.md)
