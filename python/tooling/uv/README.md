# uv

Управление проектом Python: интерпретатор, окружение, зависимости и lock-файл.
Ускорение зависит от проекта, сети и кэша; универсальных численных гарантий здесь нет.

| Параметр | Значение |
| --- | --- |
| Проверенная версия | uv 0.12.13; команды сверены также с установленным `uv help` |
| Предпосылки | Установленный uv; Python для учебного offline-примера |
| Сверено с документацией | 2026-11-06, официальная документация Astral; сайт может описывать более новую версию |
| Выполнено | 2026-11-06, uv 0.12.13, CPython 3.14.7, macOS; offline init/lock/sync/run/export и отказ при устаревшем lock |

## Навигация

- [Быстрый поиск](#быстрый-поиск)
- [Базовый уровень](#базовый-уровень)
- [Средний уровень](#средний-уровень)
- [Продвинутый уровень](#продвинутый-уровень)
- [Частые ошибки](#частые-ошибки)
- [Источники](#источники)
- [Проект, зависимости и воспроизводимость](projects.md)
- [CI, Docker, кэш и диагностика](automation.md)

## Быстрый поиск

Отдельные команды для своего проекта; установка и обновление зависимостей меняют окружение и lock-файл.

| Задача | Команда | Подробнее |
| --- | --- | --- |
| Создать приложение | `uv init my-project` | [Проект](projects.md) |
| Добавить зависимость | `uv add requests` | [Зависимости](projects.md#добавить-обновить-и-удалить) |
| Добавить инструменты разработки | `uv add --dev pytest ruff` | [Группы](projects.md#группы-и-платформы) |
| Синхронизировать | `uv sync --locked` | [Lock](projects.md#lock-не-равен-окружению) |
| Выполнить команду | `uv run --locked python main.py` | [Проект](projects.md) |
| Обновить пакет | `uv lock --upgrade-package requests` | [Обновления](projects.md#добавить-обновить-и-удалить) |
| Экспортировать с хэшами | `uv export --locked -o requirements.txt` | [Экспорт](projects.md#экспорт-и-интерфейс-pip) |
| Проверить типы | `uv check` — использует ty | [Проверки](#средний-уровень) |
| Форматировать | `uv format` — использует Ruff | [Проверки](#средний-уровень) |
| Проверить известные уязвимости | `uv audit` — требует сеть | [Диагностика](automation.md#диагностика) |

## Базовый уровень

### Начать проект

Выбери способ установки по [инструкции Astral](https://docs.astral.sh/uv/getting-started/installation/):
отдельный установщик, поддерживаемый менеджер пакетов либо `python -m pip install uv`
в подходящее окружение. Установщик выполняет скачанный код; сначала изучи инструкцию и источник.
Проверь `uv --version` и `uv help` — отдельные возможности зависят от версии.

`uv run` управляет окружением проекта без ручной активации. `uv venv` нужен для отдельного
окружения; активация в Bash/Zsh — `source .venv/bin/activate`, в PowerShell —
`.venv\Scripts\Activate.ps1`, в cmd.exe — `.venv\Scripts\activate.bat`.
Не смешивай команды разных оболочек.

[Полный offline-рецепт](projects.md#учебный-проект-без-сети) не скачивает Python или пакеты.

## Средний уровень

### Уточнить окружение и проверки

`uv python list` показывает найденные/доступные версии; `uv python install 3.14` скачивает Python.
`uv python pin 3.14` пишет запрос версии в `.python-version`, а не системный путь по умолчанию.
Ограничение поддерживаемого Python для проекта задаёт `project.requires-python` в `pyproject.toml`.

В uv 0.12.13 `uv check` запускает проверку типов через ty, `uv format` — форматирование Ruff.
Это не универсальный lint и не сортировка импортов. Для последних добавь Ruff как dev-зависимость
и используй `uv run ruff check .` / `uv run ruff check --select I --fix .`.
Исправляющая команда меняет файлы, поэтому просматривай diff.
`uv run pytest -n auto` требует установленного `pytest-xdist`; сами тесты — в [pytest](../../testing/pytest/README.md).

## Продвинутый уровень

### Повторять сборки и диагностировать проблемы

Коммить `pyproject.toml` и `uv.lock`, фиксируй uv и Python в CI, используй `--locked` для проверки
актуальности lock. `--frozen` использует существующий lock, не проверяя его соответствие проекту.
Production-установка часто исключает dev-группу; дополнительные default groups учитывай отдельно.

[CI/Docker](automation.md) показывают границы сборки; [кэш и TLS](automation.md#диагностика)
требуют диагностики, а не автоматического отключения проверок. Workspaces объединяют несколько
Python-пакетов с общим lock; это не общий менеджер всех языков monorepo.

## Частые ошибки

| Ошибка исходных рецептов | Корректный путь для uv 0.12.13 |
| --- | --- |
| `uv update`, `uv sort`, `uv info`, `uv outdated`, `uv show` | `lock --upgrade`, Ruff, `uv help`, `uv pip list --outdated`, `uv pip show` |
| `uv sync --parallel` | Операции уже используют внутренний параллелизм; при необходимости настрой documented concurrency |
| `uv sync --optimize` | Если нужен bytecode: `uv sync --compile-bytecode`; это не оптимизатор зависимостей |
| `uv cache info` | `uv cache dir`, `uv cache size` |
| Комментарий «с хэшами» у `--no-hashes` | Этот флаг удаляет хэши |
| Миграция Poetry якобы использует его lock автоматически | `uv.lock` — отдельный формат; миграцию и новое разрешение зависимостей проверяют отдельно |

## Источники

- [CLI uv](https://docs.astral.sh/uv/reference/cli/), [версии Python](https://docs.astral.sh/uv/concepts/python-versions/).
- [Lock/sync](https://docs.astral.sh/uv/concepts/projects/sync/), [зависимости](https://docs.astral.sh/uv/concepts/projects/dependencies/).
- [GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/).
- [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/), [кэш](https://docs.astral.sh/uv/concepts/cache/).

[Каталог Python](../../README.md)
