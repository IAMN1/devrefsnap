# Проект, зависимости и воспроизводимость uv

Уровень: базовый и средний.
Предпосылки: uv 0.12.13, Python.
Для установки пакетов нужен доступ к индексу.
[К справочнику uv](README.md).

## Учебный проект без сети

Полный Bash-пример предназначен для macOS/GNU/Linux с установленным `python3`.
Пример проверяет lock и окружение.
Пример не устанавливает пакеты.
Пример не меняет системный Python.
Запустите `bash project.sh`.

<!-- example: uv/project.sh -->
```bash
#!/usr/bin/env bash
set -euo pipefail
task_dir=$(mktemp -d "${TMPDIR:-/tmp}/uv-project.XXXXXX")
trap 'rm -rf -- "$task_dir"' EXIT
export UV_CACHE_DIR="$task_dir/cache" UV_PYTHON_DOWNLOADS=never
export UV_NO_CONFIG=1
python_bin=$(command -v python3)
uv init --bare --no-workspace --python "$python_bin" "$task_dir/project"
cd "$task_dir/project"
uv lock --offline --python "$python_bin"
uv sync --offline --locked --python "$python_bin"
uv run --offline --locked python -c 'import sys; assert sys.prefix != sys.base_prefix; print("venv OK")'
uv export --offline --locked --format requirements.txt -o requirements.txt
cp pyproject.toml pyproject.saved
"$python_bin" - <<'EDIT'
from pathlib import Path
p = Path('pyproject.toml')
text = p.read_text()
assert 'version = "0.1.0"' in text
p.write_text(text.replace('version = "0.1.0"', 'version = "0.2.0"'))
EDIT
if uv sync --offline --locked >"$task_dir/stale.log" 2>&1; then
    printf 'ERROR: stale lock accepted\n' >&2
    exit 1
fi
grep -q 'lockfile.*needs to be updated' "$task_dir/stale.log"
mv pyproject.saved pyproject.toml
uv sync --offline --locked
printf 'uv project OK\n'
```

Сначала ожидается `venv OK`.
Затем ожидается отказ синхронизации несогласованного проекта.
Последний результат — `uv project OK`.
Зависимостей здесь нет, поэтому экспорт не демонстрирует реальные package hashes.
Проверка скачивания пакетов и интерпретаторов этим сценарием не покрыта.

## Добавить, обновить и удалить

Ниже приведены отдельные фрагменты для проекта.
Фрагменты требуют сети или доступного кэша.
Перед принятием обновлений просмотрите diff `pyproject.toml`/`uv.lock`.
Запустите тесты.

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

`add`/`remove` меняют декларацию зависимостей и обычно lock/окружение.
`lock --upgrade` обновляет допустимые версии в рамках ограничений проекта.
Команда не снимает, например, верхнюю границу версии из `pyproject.toml`.

## Lock не равен окружению

`uv lock` рассчитывает разрешение и записывает `uv.lock`.
`uv sync` приводит окружение к выбранным зависимостям.
По умолчанию sync удаляет посторонние пакеты из управляемого окружения.
`uv run` обычно проверяет lock и синхронизирует окружение перед командой.

| Режим | Что проверяет/меняет |
| --- | --- |
| Обычный `sync` | При необходимости обновляет lock и окружение |
| `sync --locked` | Отказывает, если lock отсутствует или не соответствует проекту |
| `sync --frozen` | Использует lock без проверки соответствия декларации |
| `run --no-sync` | Не синхронизирует окружение; ответственность за его состояние у вызывающего |

## Группы и платформы

Фрагмент `pyproject.toml`, дополняющий метаданные существующего проекта:

```toml
[dependency-groups]
dev = ["pytest", "ruff"]

[project.optional-dependencies]
excel = ["openpyxl"]
```

`uv sync --extra excel` включает extra.
Группа `dev` включена по умолчанию.
`--no-dev` исключает `dev`, но не обязательно все настроенные default groups.
Для исключения всех default groups используйте `--no-default-groups`.
Настройка `--group` добавляет нужную группу явно.

Задавайте платформенную зависимость через marker.
Имя extra «windows» само не выбирает ОС:

```toml
[project]
name = "platform-demo"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = ["pywin32; sys_platform == 'win32'"]
```

Это самостоятельный фрагмент метаданных для демонстрации marker.
В реальном проекте не дублируйте `[project]`.
Универсальное разрешение lock не доказывает, что native wheel доступен на каждой целевой системе.

## Экспорт и интерфейс pip

Фрагменты, не заменяющие основной `uv.lock`:

```bash
uv export --locked --format requirements.txt -o requirements.txt
uv export --locked --no-hashes -o requirements-without-hashes.txt
uv pip show pytest
uv pip list --outdated
uv pip freeze
```

Экспорт requirements по умолчанию содержит хэши там, где они доступны.
`--no-hashes` убирает хэши.
`uv pip` работает с окружением и не является командой изменения зависимостей проекта.
Для legacy requirements создайте `uv venv`.
Затем выполните `uv pip install -r requirements.txt`.
`uv pip compile` и `uv pip sync` обслуживают соответствующий workflow.
При миграции с Poetry перенесите constraints, groups, sources и package metadata.
Создайте новый lock.
Проверьте поведение.
Не считайте `poetry.lock` автоматически эквивалентным `uv.lock`.

## Источники

[Управление зависимостями](https://docs.astral.sh/uv/concepts/projects/dependencies/),
[lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/),
[интерфейс pip](https://docs.astral.sh/uv/pip/), [экспорт](https://docs.astral.sh/uv/concepts/projects/export/).
Сверка: 2026-11-06. Выполнен только приведённый offline-сценарий, uv 0.12.13 / Python 3.14.7.
