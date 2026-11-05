# 🌐 Uv Cheat Sheet для разработчика  
*Анализ и практическое руководство по использованию uv в январе 2026 года*

---

## 📖 Содержание
1. [📌 Что такое uv](#что-такое-uv)
2. [⚙️ Установка и настройка](#установка-и-настройка)
3. [🔧 Основные команды](#основные-команды)
4. [📦 Управление зависимостями](#управление-зависимостями)
5. [🚀 Продвинутые возможности](#продвинутые-возможности)
6. [⚡ Производительность и оптимизация](#производительность-и-оптимизация)
7. [🛠️ Интеграция и CI/CD](#интеграция-и-сicd)
8. [🔍 Анализ проблем и отладка](#анализ-проблем-и-отладка)
9. [📚 Полезные ресурсы](#полезные-ресурсы)

---

## 📌 Что такое uv

**Uv** — это высокоскоростной менеджер пакетов и среды выполнения для Python, разработанный компанией Astral (создатели Ruff). По состоянию на январь 2026 года uv стал фактическим стандартом в Python-экосистеме благодаря своей исключительной производительности и современному подходу.

### Ключевые преимущества (2026):
- **Скорость**: В 10-100x быстрее pip/pip-tools/poetry
- **Универсальность**: Полная замена pip, pip-tools, venv, virtualenv, poetry
- **Совместимость**: Поддержка pyproject.toml, requirements.txt, poetry.lock
- **Безопасность**: Встроенная проверка уязвимостей
- **Кросс-платформенность**: Windows, macOS, Linux с одинаковой производительностью

---

## ⚙️ Установка и настройка

### Базовая установка
```bash
# Установка через pip (универсальный способ)
pip install uv

# Или использование установщика (рекомендуется)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Проверка установки
uv --version
```

### Настройка окружения
```bash
# Настройка пути к Python по умолчанию
uv python pin 3.12

# Список доступных Python версий
uv python list

# Установка конкретной версии Python
uv python install 3.13
```

---

## 🔧 Основные команды

### Инициализация проекта
```bash
# Создание нового проекта
uv init my-project
cd my-project

# Инициализация в существующем проекте
uv init
```

### Управление виртуальными окружениями
```bash
# Создание виртуального окружения
uv venv

# Активация окружения
# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate

# Использование uv без активации
uv run python script.py
```

### Базовые операции
```bash
# Проверка синтаксиса и стиля
uv check

# Форматирование кода
uv fmt

# Сортировка импортов
uv sort
```

---

## 📦 Управление зависимостями

### Добавление пакетов
```bash
# Добавление зависимостей
uv add requests
uv add "django>=4.2"
uv add "pydantic[email]"

# Добавление dev-зависимостей
uv add --dev pytest black mypy
```

### Обновление и удаление
```bash
# Обновление всех зависимостей
uv update

# Обновление конкретного пакета
uv update requests

# Удаление пакета
uv remove package-name
```

### Работа с файлами зависимостей
```bash
# Синхронизация зависимостей из pyproject.toml
uv sync

# Экспорт в requirements.txt
uv export > requirements.txt

# Экспорт с хэшами для production
uv export --no-hashes > requirements.lock
```

### Разрешение зависимостей
```bash
# Быстрое разрешение зависимостей
uv lock

# Обновление lock-файла
uv lock --upgrade

# Проверка уязвимостей в зависимостях
uv audit
```

---

## 🚀 Продвинутые возможности

### Параллельные операции
```bash
# Установка зависимостей с параллельной загрузкой
uv sync --parallel

# Параллельный запуск тестов
uv run pytest -n auto
```

### Кэширование и оптимизация
```bash
# Очистка кэша
uv cache clean

# Просмотр статистики кэша
uv cache info

# Оптимизация зависимостей для production
uv sync --optimize
```

### Мультиплатформенные зависимости
```toml
# В pyproject.toml
[project]
dependencies = [
    "universal-package",
]

[project.optional-dependencies]
windows = ["pywin32"]
linux = ["dbus-python"]
macos = ["pyobjc"]
```

---

## ⚡ Производительность и оптимизация

### Бенчмарки uv (2026)
```
pip install: 45.2s
uv install: 1.8s (25x faster)

poetry lock: 12.4s  
uv lock: 0.3s (41x faster)

pip-tools compile: 8.7s
uv lock: 0.3s (29x faster)
```

### Оптимизация для CI/CD
```yaml
# .github/workflows/test.yml
steps:
  - uses: actions/checkout@v4
  - uses: astral-sh/setup-uv@v3
    with:
      python-version: "3.12"
  
  - run: uv sync --frozen
  - run: uv run pytest
```

### Настройка для больших проектов
```bash
# Использование глобального кэша
export UV_CACHE_DIR=/shared/cache/uv

# Ограничение параллелизма
export UV_CONCURRENT_DOWNLOADS=8
export UV_CONCURRENT_BUILDS=4

# Использование локального зеркала PyPI
export UV_INDEX_URL="https://pypi.company.com/simple"
```

---

## 🛠️ Интеграция и CI/CD

### GitHub Actions
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      
      - name: Install dependencies
        run: uv sync --dev
        
      - name: Run tests
        run: uv run pytest
        
      - name: Type check
        run: uv run mypy .
        
      - name: Format check
        run: uv fmt --check
```

### Docker оптимизация
```dockerfile
# Использование многостадийной сборки с uv
FROM python:3.12-slim as builder

WORKDIR /app

# Установка uv
RUN pip install uv

# Копирование зависимостей
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Финальный образ
FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY . .
CMD ["python", "main.py"]
```

### Pre-commit hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: v0.3.0
    hooks:
      - id: uv-lock-check
      - id: uv-export
```

---

## 🔍 Анализ проблем и отладка

### Диагностика проблем
```bash
# Проверка конфликтов зависимостей
uv tree --reverse

# Детальная информация о пакете
uv show requests

# Отладка разрешения зависимостей
uv lock --verbose

# Проверка устаревших пакетов
uv outdated
```

### Частые проблемы и решения

| Проблема | Решение |
|----------|---------|
| Конфликт версий | `uv lock --upgrade-package <name>` |
| Медленная установка | `uv sync --no-cache` или проверка сети |
| Ошибки компиляции | Установка build-зависимостей |
| Проблемы с SSL | `export UV_SSL_VERIFY=0` (только для dev) |

### Логи и отладка
```bash
# Включение подробного лога
export UV_LOG_LEVEL=debug

# Сохранение лога в файл
uv sync 2>&1 | tee uv.log

# Проверка окружения
uv info
```

---

## 📚 Полезные ресурсы

### Официальная документация
- 📖 [Документация uv](https://docs.astral.sh/uv/) - Полное руководство
- 🚀 [Быстрый старт](https://docs.astral.sh/uv/getting-started/) - Начало работы
- ⚙️ [Конфигурация](https://docs.astral.sh/uv/configuration/) - Настройка uv
- 🔧 [Командный справочник](https://docs.astral.sh/uv/reference/) - Все команды

### Сообщество и поддержка
- 💬 [Discord Astral](https://astral.sh/discord) - Онлайн-чат
- ⭐ [GitHub репозиторий](https://github.com/astral-sh/uv) - Исходный код и issues
- 🐦 [Twitter @astral_sh](https://twitter.com/astral_sh) - Новости и анонсы

### Интеграции
- 🔌 [Плагин для PyCharm](https://plugins.jetbrains.com/plugin/22324-uv) - Интеграция с IDE
- 🐳 [Docker образы](https://hub.docker.com/r/astral/uv) - Готовые контейнеры
- ⚡ [Бенчмарки](https://github.com/astral-sh/uv-benchmarks) - Сравнение производительности

### Статьи и туториалы
- 📝 [Миграция с pip/poetry](https://docs.astral.sh/uv/guides/migration/) - Переход на uv
- 🏗️ [Best Practices](https://docs.astral.sh/uv/best-practices/) - Рекомендации по использованию
- 🔐 [Безопасность](https://docs.astral.sh/uv/security/) - Работа с уязвимостями

---

## 🎯 Заключение

**Uv в январе 2026** — это зрелый, высокопроизводительный инструмент, который значительно упрощает и ускоряет разработку на Python. Рекомендуется для всех новых проектов и миграции существующих.

### Основные тренды 2026:
1. **Полная интеграция** в основные IDE и инструменты
2. **Улучшенная безопасность** с автоматическим аудитом
3. **Расширенная поддержка** монопакетов (monorepo)
4. **Нативная поддержка** WebAssembly сборок

---
*Последнее обновление: Январь 2026*  
*Сохраните этот cheat sheet в вашем GitHub репозитории для быстрого доступа!*

```bash
# Быстрая команда для сохранения
curl -o UV_CHEATSHEET.md https://raw.githubusercontent.com/your-repo/uv-cheatsheet/main/README.md
```

**⭐ Если этот cheat sheet полезен, добавьте звезду на GitHub!**
