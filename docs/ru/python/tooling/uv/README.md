
# uv

[English](../../../../en/python/tooling/uv/README.md)

Используйте uv для управления интерпретатором, окружением, зависимостями и lock-файлом проекта Python.
Ускорение зависит от проекта, сети и кэша.
Материал не даёт универсальных численных гарантий.


## Быстрый поиск

Выполняйте отдельные команды в своём проекте.
Установка и обновление зависимостей меняют окружение и lock-файл.

| Задача | Команда | Подробнее |
| --- | --- | --- |
| Создать приложение | `uv init my-project` | [Проект](projects.md) |
| Добавить зависимость | `uv add requests` | [Зависимости](projects.md#добавить-обновить-и-удалить) |
| Добавить инструменты разработки | `uv add --dev pytest ruff` | [Группы](projects.md#группы-и-платформы) |
| Синхронизировать | `uv sync --locked` | [Lock](projects.md#lock-не-равен-окружению) |
| Выполнить команду | `uv run --locked python main.py` | [Проект](projects.md) |
| Обновить пакет | `uv lock --upgrade-package requests` | [Обновления](projects.md#добавить-обновить-и-удалить) |
| Экспортировать с хэшами | `uv export --locked -o requirements.txt` | [Экспорт](projects.md#экспорт-и-интерфейс-pip) |
| Проверить типы | `uv check` — использует ty | [Проверки](#уточнить-окружение-и-проверки) |
| Форматировать | `uv format` — использует Ruff | [Проверки](#уточнить-окружение-и-проверки) |
| Проверить известные уязвимости | `uv audit` — требует сеть | [Диагностика](automation.md#диагностика) |

| Параметр | Значение |
| --- | --- |
| Версия команд | uv 0.12.13 |
| Предпосылки | Установленный uv; Python для учебного offline-примера |

<a id="навигация"></a>

<a id="базовый-уровень"></a>


## Начать проект

**Ситуация:** нужно создать новое приложение и запускать Python из его окружения.
**Изменение:** выполните фрагмент в каталоге, где `my-project` ещё не существует:

```bash
uv init my-project
cd my-project
uv sync
uv run python -c 'import sys; print(sys.prefix)'
```

**Результат:** uv создаёт проект, lock-файл и окружение `.venv`; команда выводит путь окружения.
Команды могут скачать Python и зависимости.
[Полный offline-сценарий](projects.md#учебный-проект-без-сети) использует уже установленный Python.


Выберите способ установки по [инструкции Astral](https://docs.astral.sh/uv/getting-started/installation/):
отдельный установщик, поддерживаемый менеджер пакетов либо `python -m pip install uv`
в подходящее окружение.
Установщик выполняет скачанный код.
Сначала изучите инструкцию и источник.
Проверьте `uv --version`.
Проверьте `uv help`.
Отдельные возможности зависят от версии.

`uv run` управляет окружением проекта без ручной активации.
`uv venv` нужен для отдельного окружения.
Для активации в Bash/Zsh используйте `source .venv/bin/activate`.
В PowerShell используйте `.venv\Scripts\Activate.ps1`.
В cmd.exe используйте `.venv\Scripts\activate.bat`.
Не смешивайте команды разных оболочек.

[Полный offline-рецепт](projects.md#учебный-проект-без-сети) не скачивает Python или пакеты.

<a id="средний-уровень"></a>


## Уточнить окружение и проверки

**Ситуация:** в проект нужно добавить pytest, сохранив зависимость в декларации и lock-файле.
**Изменение:** используйте dev-группу вместо ручного `pip install` в `.venv`.
Фрагмент для существующего uv-проекта:

```bash
uv add --dev pytest
uv run --locked python -m pytest
```

**Результат:** pytest входит в dev-группу, а тесты запускаются в окружении проекта.
Добавление пакета требует доступного индекса или кэша.
Сами тестовые файлы должны существовать.
[Группы и платформы](projects.md#группы-и-платформы).


`uv python list` показывает найденные и доступные версии.
`uv python install 3.14` скачивает Python.
`uv python pin 3.14` пишет запрос версии в `.python-version`, а не системный путь по умолчанию.
Ограничение поддерживаемого Python для проекта задаёт `project.requires-python` в `pyproject.toml`.

В uv 0.12.13 `uv check` запускает проверку типов через ty.
Команда `uv format` запускает форматирование Ruff.
Эти команды не выполняют универсальный lint или сортировку импортов.
Для lint и сортировки импортов добавьте Ruff как dev-зависимость.
Используйте `uv run ruff check .` / `uv run ruff check --select I --fix .`.
Исправляющая команда меняет файлы.
Просматривайте diff после исправления.
`uv run pytest -n auto` требует установленного `pytest-xdist`.
Сами тесты разобраны в [pytest](../../testing/pytest/README.md).

<a id="продвинутый-уровень"></a>


## Повторять сборки и диагностировать проблемы

**Ситуация:** CI должен отказать, если `pyproject.toml` расходится с сохранённым lock-файлом.
**Изменение:** используйте `--locked` при синхронизации и запуске.
Фрагмент для проекта с dev-зависимостью pytest:

```bash
uv sync --locked
uv run --locked pytest
```

**Результат:** несогласованный lock вызывает отказ; согласованный lock задаёт выбранные версии пакетов.
`--frozen` пропускает проверку соответствия декларации и не заменяет это условие CI.
[Полная конфигурация CI](automation.md#github-actions).


Добавляйте `pyproject.toml` и `uv.lock` в коммит.
Фиксируйте uv и Python в CI.
Production-установка часто исключает dev-группу.
Учитывайте дополнительные default groups отдельно.

[CI/Docker](automation.md) показывают границы сборки.
При проблемах с [кэшем и TLS](automation.md#диагностика) проведите диагностику.
Не отключайте проверки автоматически.
Workspaces объединяют несколько Python-пакетов с общим lock.
Workspaces не являются общим менеджером всех языков monorepo.


## Частые ошибки

| Неподходящая команда или ожидание | Используйте в uv 0.12.13 |
| --- | --- |
| `uv update`, `uv sort`, `uv info`, `uv outdated`, `uv show` | `lock --upgrade`, Ruff, `uv help`, `uv pip list --outdated`, `uv pip show` |
| `uv sync --parallel` | Операции уже используют внутренний параллелизм. При необходимости настройте documented concurrency |
| `uv sync --optimize` | Если нужен bytecode, используйте `uv sync --compile-bytecode`. Это не оптимизатор зависимостей |
| `uv cache info` | `uv cache dir`, `uv cache size` |
| Комментарий «с хэшами» у `--no-hashes` | Этот флаг удаляет хэши |
| Миграция Poetry якобы использует его lock автоматически | `uv.lock` — отдельный формат; миграцию и новое разрешение зависимостей проверяют отдельно |


## Источники

- [CLI uv](https://docs.astral.sh/uv/reference/cli/), [версии Python](https://docs.astral.sh/uv/concepts/python-versions/).
- [Lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/), [зависимости](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/).
- [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/), [кэш](https://docs.astral.sh/uv/concepts/cache/).

[Каталог Python](../../README.md)
