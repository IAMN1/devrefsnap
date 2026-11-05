# CI, Docker, кэш и диагностика uv

Уровень: продвинутый. Предпосылки: работающий проект с `pyproject.toml`, `uv.lock` и тестами.
[К справочнику uv](README.md).

## GitHub Actions

Фрагмент шагов внутри job на подходящем runner; YAML сверён с документацией, workflow не запускался.
Actions refs нужно отдельно проверять/фиксировать по политике проекта; эти major refs — пример настройки.

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

Проект должен объявлять pytest и Ruff в dev-группе. `uv format` использует собственный механизм
запуска Ruff; для единственной фиксированной версии форматтера из lock можно вместо него
запускать `uv run --locked ruff format --check .`.
Lock не заменяет проверку Python/платформы runner; тестируй поддерживаемые сочетания матрицей.

## Docker

Полный образец для простого непакетируемого приложения с `main.py` в корне.
Файлы проекта должны существовать до сборки; Docker build/runtime **не выполнялись**.
В Dockerfile оба Python-образа должны иметь совместимые пути, ОС и архитектуру;
для воспроизводимой production-сборки фиксируют также digest образов.

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

Для пакета с `src/` сначала установи зависимости с `--no-install-project`, затем скопируй код
и установи проект `uv sync --locked --no-dev --no-editable`; один перенос venv до установки пакета
не заменяет этот шаг. Нужны также политика non-root, writable paths и обработка сигналов приложения.
Не копируй локальную `.venv` в Linux-образ; добавь её в `.dockerignore`.

## Проверка lock в pre-commit

Фрагмент `.pre-commit-config.yaml`; pre-commit должен быть установлен отдельно, uv — доступен в PATH.
Используется локальный check без автоматической перезаписи lock. Хук **не запускался**.

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

Официальный [uv-pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/) также предоставляет
хуки генерации lock/export; их IDs и rev выбирают по версии репозитория, а не придумывают.

## Кэш и параллелизм

Отдельные операции: `uv cache dir`, `uv cache size`, `uv cache prune`.
`uv cache clean` удаляет кэш и может сделать следующий запуск медленнее; это не обычная оптимизация.
`--no-cache` обходит кэш и полезен для диагностики его влияния, а не как универсальное ускорение.

Фрагмент окружения job, пути адаптируй и обеспечь доступ только нужным пользователям:

```bash
export UV_CACHE_DIR=/path/to/job/cache
export UV_CONCURRENT_DOWNLOADS=8
export UV_CONCURRENT_BUILDS=4
```

Доступный параллелизм ограничивают ресурсами runner и сервиса пакетов.
Для собственных сравнений фиксируй команды, lock, Python, платформу, сеть и состояние cold/warm cache.
Сравнение `pip install` и `uv lock` измеряет разные задачи и не доказывает ускорение установки.

## Диагностика

| Задача | Действие |
| --- | --- |
| Почему выбрана зависимость | `uv tree --reverse` |
| Логи разрешения | `uv -v lock`; не публиковать логи без просмотра URL/данных |
| Обновить конкретный кандидат | `uv lock --upgrade-package NAME`; несовместимые constraints этим не снимаются |
| Проверить environment dependencies | `uv pip check` |
| Известные уязвимости | `uv audit`; нужен сетевой доступ, результат зависит от источников advisory |
| Корпоративный индекс | `UV_DEFAULT_INDEX` / настройка index; не помещать credentials в коммит |
| TLS failure | Проверить имя сервера, время и цепочку CA; при необходимости `--system-certs` или `SSL_CERT_FILE` по документации |

`UV_INDEX_URL` — старое имя настройки; установленный uv рекомендует `UV_DEFAULT_INDEX`.
`UV_SSL_VERIFY=0` и `UV_LOG_LEVEL` не являются рецептами из проверенного help.
Не отключай проверку TLS ради того, чтобы установка «заработала»; это меняет доверие к коду пакетов.

## Источники и границы проверки

[CI](https://docs.astral.sh/uv/guides/integration/github/), [Docker](https://docs.astral.sh/uv/guides/integration/docker/),
[pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/), [TLS](https://docs.astral.sh/uv/concepts/authentication/certificates/),
[environment variables](https://docs.astral.sh/uv/reference/environment/).
Сверка: 2026-11-06. В CI, Docker, pre-commit и внешних индексах выполнение не проводилось;
локально сверены help uv 0.12.13 и [offline-проект](projects.md).
