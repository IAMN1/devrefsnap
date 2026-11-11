<a id="проект-зависимости-и-воспроизводимость-uv"></a>
# Projects, dependencies, and reproducibility with uv

[Русский](../../../../ru/python/tooling/uv/projects.md)

Use this page to create a project, change dependencies, or verify lockfile consistency.
The dependency-changing commands apply to a separate practice project.

| Task | Technique | Example / details |
| --- | --- | --- |
| Create a project without downloading packages | `uv init`, `lock`, `sync --locked` | [Complete offline scenario](#offline-practice-project) |
| Change dependencies | `uv add`, `remove`, `lock --upgrade-package` | [Package changes](#add-upgrade-and-remove-dependencies) |
| Choose a lockfile check | Compare `--locked` and `--frozen` | [Mode table](#lockfile-and-environment) |
| Choose groups or export | `--group`, `--extra`, `uv export` | [Groups](#groups-and-platforms) · [Export](#export-and-the-pip-interface) |

Beginner and intermediate levels.
Requires uv 0.12.13 and Python.
Package installation requires access to an index.
[uv reference](README.md).

<a id="учебный-проект-без-сети"></a>
## Offline practice project

The complete Bash example is for macOS or GNU/Linux with `python3` installed.
It checks the lockfile and environment without installing packages or changing the system Python.
Run `bash project.sh`.

[`uv/project.sh`](../../../../../examples/python/tooling/uv/project.sh)

First, expect `venv OK`.
Next, expect synchronization to fail for an inconsistent project.
The final result is `uv project OK`.
There are no dependencies here, so the export does not demonstrate actual package hashes.
The reference shows package and interpreter downloads. This scenario runs offline.

<a id="добавить-обновить-и-удалить"></a>
## Add, upgrade, and remove dependencies

The following are separate project snippets.
The snippets require network access or an accessible cache.
Review the `pyproject.toml` and `uv.lock` diff before accepting updates.
Run the tests.

```bash
uv add requests
uv add 'django>=5.2'
uv add 'pydantic[email]'
uv add --dev pytest ruff
uv lock --upgrade
uv lock --upgrade-package requests
uv sync --locked
uv remove requests
```

`add` and `remove` change the dependency declaration and usually the lockfile and environment.
`lock --upgrade` updates eligible versions within the project's constraints.
For example, an upper version bound in `pyproject.toml` still applies.

<a id="lock-не-равен-окружению"></a>
## Lockfile and environment

`uv lock` resolves dependencies and writes `uv.lock`.
`uv sync` brings the environment into line with the selected dependencies.
By default, sync removes extraneous packages from the managed environment.
`uv run` usually checks the lockfile and synchronizes the environment before running the command.

| Mode | What it checks or changes |
| --- | --- |
| Regular `sync` | Updates the lockfile and environment if necessary |
| `sync --locked` | Fails if the lockfile is missing or inconsistent with the project |
| `sync --frozen` | Uses the lockfile without checking whether it matches the declaration |
| `run --no-sync` | Skips environment synchronization. The caller is responsible for its state |

<a id="группы-и-платформы"></a>
## Groups and platforms

This `pyproject.toml` fragment adds to the metadata of an existing project.

```toml
[dependency-groups]
dev = ["pytest", "ruff"]

[project.optional-dependencies]
excel = ["openpyxl"]
```

`uv sync --extra excel` includes the extra.
The `dev` group is included by default.
`--no-dev` excludes `dev`. Other configured default groups may still be included.
To exclude every default group, use `--no-default-groups`.
`--group` adds the specified group explicitly.

Define platform-dependent requirements with a marker.
An extra named `windows` requires a marker to select the operating system.

```toml
[project]
name = "platform-demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["pywin32; sys_platform == 'win32'"]
```

This standalone metadata fragment demonstrates a marker.
In an existing project, add the fields to the existing `[project]` table.
Universal lockfile resolution does not prove that a native wheel is available on every target system.

<a id="экспорт-и-интерфейс-pip"></a>
## Export and the pip interface

These snippets supplement the primary `uv.lock` file.

```bash
uv export --locked --format requirements.txt -o requirements.txt
uv export --locked --no-hashes -o requirements-without-hashes.txt
uv pip show pytest
uv pip list --outdated
uv pip freeze
```

Requirements exports include hashes where available by default.
`--no-hashes` removes hashes.
`uv pip` operates on the environment. Change project dependencies with the project commands.
For legacy requirements, create an environment with `uv venv`.
Then run `uv pip install -r requirements.txt`.
`uv pip compile` and `uv pip sync` support that workflow.
When migrating from Poetry, transfer constraints, groups, sources, and package metadata.
Create a new lockfile.
Check behavior.
Treat `poetry.lock` and `uv.lock` as separate formats.

<a id="источники"></a>
## Sources

[Dependency management](https://docs.astral.sh/uv/concepts/projects/dependencies/),
[lock and sync](https://docs.astral.sh/uv/concepts/projects/sync/),
[pip interface](https://docs.astral.sh/uv/pip/), [export](https://docs.astral.sh/uv/concepts/projects/export/).
