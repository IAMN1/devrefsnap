# Конфигурация, плагины, отладка и CI pytest

Откройте страницу, чтобы выбрать тесты, зарегистрировать markers или настроить отчёты.
Различайте встроенные команды pytest и возможности установленных плагинов.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Настроить сбор и markers | `pytest.ini`, `--strict-markers` | [Конфигурация](#настроить-сбор-тестов-и-markers) |
| Повторить падение | `--lf`, `-x`, `--tb=short` | [Отладка](#выбор-тестов-и-отладка) |
| Получить отчёт или параллельность | JUnit либо отдельный плагин | [Плагины](#плагины-и-отчёты) |
| Воспроизвести примеры | Отдельное окружение с фиксированными пакетами | [Версии](#среда-примеров) |

Уровень: средний и продвинутый.
Предпосылки: тесты и установленный pytest в окружении проекта.
[К справочнику pytest](README.md).

## Настроить сбор тестов и markers

Полный `pytest.ini` для учебных файлов этой темы:

<!-- example: pytest/pytest.ini -->
```ini
[pytest]
minversion = 9.0
testpaths = .
python_files = test_*.py
addopts = --strict-markers --tb=short
asyncio_mode = strict
asyncio_default_fixture_loop_scope = function
markers =
    slow: длительные тесты
    integration: проверки нескольких компонентов
    unit: изолированные проверки поведения
```

`minversion` ограничивает **pytest**, не Python.
`asyncio_mode` требует pytest-asyncio.
Если плагин не установлен и async-тестов нет, уберите настройку.
В настоящем проекте обычно задают `testpaths = tests`.
Код `src/package` устанавливают как пакет.
Альтернатива ini — `[tool.pytest.ini_options]` в `pyproject.toml`.
Не поддерживайте расходящиеся копии конфигурации.
При необходимости добавляйте build-каталоги в `norecursedirs`.
Не скрывайте нужные тесты.

Marker можно зарегистрировать также через `config.addinivalue_line("markers", "slow: ...")` в hook `pytest_configure`.
Для обычного проекта статическая конфигурация проще.

Фрагменты для тестового модуля с `import pytest` / `import sys`:

```python
@pytest.mark.skip(reason="нужен отдельный сервис")
def test_external_service():
    raise AssertionError("этот тест намеренно пропущен")

@pytest.mark.skipif(sys.platform == "win32", reason="проверяется Unix-поведение")
def test_unix_path():
    assert sys.platform != "win32"

@pytest.mark.xfail(strict=True, reason="воспроизводится issue #123")
def test_known_regression():
    assert 2 + 2 == 5
```

Это отдельные примеры механизмов, а не основной исполняемый комплект.
`xfail(strict=True)` превращает неожиданное прохождение в ошибку.
После исправления уберите marker.
Skip не доказывает исправность функции.

## Выбор тестов и отладка

Ниже приведены отдельные команды.
Необязательные debug-флаги могут открыть интерактивный отладчик.

```bash
python -m pytest --collect-only
python -m pytest -k 'subtotal'
python -m pytest -m 'not slow'
python -m pytest -x
python -m pytest --lf
python -m pytest --ff
python -m pytest --sw
python -m pytest -s -v
python -m pytest --durations=10
python -m pytest -rs
```

`--lf` использует кэш последнего падения.
Когда записи отсутствуют, по умолчанию могут запускаться все тесты.
`--ff` запускает прежние падения первыми.
`--sw` останавливается на падении и сохраняет точку продолжения.
`-s` отключает capture.
С xdist захват вывода имеет дополнительные ограничения.
`--pdb` входит в pdb при ошибке.
`--trace` входит в pdb в начале теста.
Без необходимости отдельный pytest-ipdb не нужен.
`--tb=auto|short|line|no` меняет объём traceback.
В CI не скрывайте диагностику без причины.

## Плагины и отчёты

| Возможность | Зависимость | Фрагмент команды |
| --- | --- | --- |
| JUnit XML | Встроено в pytest | `python -m pytest --junitxml=report.xml` |
| Покрытие | pytest-cov | `python -m pytest --cov=demo_service --cov-report=term-missing --cov-report=html` |
| Параллельные workers | pytest-xdist | `python -m pytest -n 2` или `-n auto` |
| Asyncio | pytest-asyncio | `python -m pytest --asyncio-mode=strict` |
| `mocker` | pytest-mock | Fixture в тесте |

Установите зависимости в существующий uv-проект: `uv add --dev pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio`.
По документации xdist, `-n auto` выбирает физические ядра.
Ограничивайте процессы ресурсами CI.
Session fixture действует в каждом worker.
Разделяйте общую внешнюю БД по worker либо избегайте shared state.
Порядок выполнения тестов не должен быть условием корректности.
Используйте pytest-order только для специально обоснованных сценариев.
Расширения параметризации вроде pytest-cases требуют собственной документации.

JUnit встроен в pytest.
JSON-отчёт тестовых результатов требует выбранного плагина.
Например, [pytest-json-report](https://github.com/numirias/pytest-json-report) использует `--json-report --json-report-file=report.json`.
Этот отчёт не равен JSON-отчёту **coverage**.
Не скрывайте все DeprecationWarning.
При обоснованной необходимости настройте узкий `filterwarnings` по категории, сообщению и модулю.
Укажите причину фильтрации.

## Среда примеров

Для воспроизведения используйте CPython 3.14.7.
Установите пакеты в отдельное окружение: `python -m pip install 'pytest==9.2.0' 'pytest-mock==3.17.0' 'pytest-asyncio==1.4.1.post1' 'pytest-cov==7.1.0' 'pytest-xdist==3.8.0'`.

Покрытие показывает исполненные строки.
Покрытие не доказывает достаточность утверждений.
Проверяйте ошибочные входы.
Проверяйте отказ внешнего адаптера.

## Источники

[Конфигурация/API](https://docs.pytest.org/en/stable/reference/reference.html),
[запуск](https://docs.pytest.org/en/stable/how-to/usage.html),
[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/reporting.html),
[xdist](https://pytest-xdist.readthedocs.io/en/stable/distribution.html).
