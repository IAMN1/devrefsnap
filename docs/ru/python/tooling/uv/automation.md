
# CI, Docker, кэш и диагностика uv

[English](../../../../en/python/tooling/uv/automation.md)

Откройте страницу, если проект с `uv.lock` нужно проверять в CI или собирать в контейнере.
Используйте диагностику, когда установка или разрешение зависимостей завершаются ошибкой.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Повторить проверки в CI | Фиксированные uv/Python и `--locked` | [GitHub Actions](#github-actions) |
| Собрать окружение приложения | Разделить builder и runtime | [Docker](#docker) |
| Проверить lock до коммита | `uv lock --check` | [Pre-commit](#проверка-lock-в-pre-commit) |
| Найти причину установки | Кэш, `uv tree`, проверка TLS | [Диагностика](#диагностика) |

Уровень: продвинутый.
Предпосылки: работающий проект с `pyproject.toml`, `uv.lock` и тестами.
[К справочнику uv](README.md).

Для первого запуска используйте [учебный проект с Docker Compose и GitHub Actions](../../../tools/compose-and-github-actions.md).


## GitHub Actions

Ниже приведён фрагмент шагов внутри job на подходящем runner.
Проверяйте Actions refs отдельно.
Фиксируйте Actions refs по политике проекта.
Указанные major refs служат примером настройки.

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

Объявите pytest и Ruff в dev-группе проекта.
`uv format` использует собственный механизм запуска Ruff.
Для единственной фиксированной версии форматтера из lock можно вместо `uv format` запускать `uv run --locked ruff format --check .`.
Lock не заменяет проверку Python и платформы runner.
Тестируйте поддерживаемые сочетания матрицей.


## Docker

Полный образец для простого непакетируемого приложения с `main.py` в корне.
Подготовьте файлы проекта до сборки.
В Dockerfile оба Python-образа должны иметь совместимые пути, ОС и архитектуру.
Для воспроизводимой production-сборки фиксируйте также digest образов.

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

Для пакета с `src/` сначала установите зависимости с `--no-install-project`.
Затем скопируйте код.
Установите проект: `uv sync --locked --no-dev --no-editable`.
Один перенос venv до установки пакета не заменяет установку проекта.
Нужны также политика non-root, writable paths и обработка сигналов приложения.
Не копируйте локальную `.venv` в Linux-образ.
Добавьте `.venv` в `.dockerignore`.


## Проверка lock в pre-commit

Ниже приведён фрагмент `.pre-commit-config.yaml`.
Установите pre-commit отдельно.
Обеспечьте доступность uv в PATH.
Фрагмент использует локальный check без автоматической перезаписи lock.

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

Официальный [uv-pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/) также предоставляет хуки генерации lock/export.
Используйте существующие IDs и rev хуков для выбранной версии репозитория.


## Кэш и параллелизм

Отдельные операции: `uv cache dir`, `uv cache size`, `uv cache prune`.
`uv cache clean` удаляет кэш.
Команда может сделать следующий запуск медленнее.
Не используйте очистку как обычную оптимизацию.
`--no-cache` обходит кэш и полезен для диагностики его влияния, а не как универсальное ускорение.

Ниже приведён фрагмент окружения job.
Адаптируйте пути.
Предоставьте доступ только нужным пользователям:

```bash
export UV_CACHE_DIR=/path/to/job/cache
export UV_CONCURRENT_DOWNLOADS=8
export UV_CONCURRENT_BUILDS=4
```

Ограничивайте доступный параллелизм ресурсами runner и сервиса пакетов.
Для собственных сравнений фиксируйте команды, lock, Python, платформу, сеть и состояние cold/warm cache.
Сравнение `pip install` и `uv lock` измеряет разные задачи и не доказывает ускорение установки.


## Диагностика

| Задача | Действие |
| --- | --- |
| Почему выбрана зависимость | `uv tree --reverse` |
| Логи разрешения | `uv -v lock`. Перед публикацией просмотрите URL и данные в логах |
| Обновить конкретный кандидат | `uv lock --upgrade-package NAME`; несовместимые constraints этим не снимаются |
| Проверить environment dependencies | `uv pip check` |
| Известные уязвимости | `uv audit`; нужен сетевой доступ, результат зависит от источников advisory |
| Корпоративный индекс | `UV_DEFAULT_INDEX` / настройка index. Не помещайте credentials в коммит |
| TLS failure | Проверьте имя сервера, время и цепочку CA. При необходимости используйте `--system-certs` или `SSL_CERT_FILE` по документации |

`UV_INDEX_URL` — старое имя настройки.
Для uv 0.12.13 используйте `UV_DEFAULT_INDEX`.
Не используйте `UV_SSL_VERIFY=0` и `UV_LOG_LEVEL` для настройки uv 0.12.13.
Не отключайте проверку TLS ради того, чтобы установка «заработала».
Отключение проверки меняет доверие к коду пакетов.


## Источники

[CI](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/),
[pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/), [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/),
[environment variables](https://docs.astral.sh/uv/reference/environment/).
