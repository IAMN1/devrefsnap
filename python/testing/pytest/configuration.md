# Конфигурация, плагины, отладка и CI pytest

Уровень: средний и продвинутый. Предпосылки: тесты и установленный pytest в окружении проекта.
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

`minversion` ограничивает **pytest**, не Python. `asyncio_mode` требует pytest-asyncio;
если плагин не установлен и async-тестов нет, убери настройку. В настоящем проекте обычно
`testpaths = tests`, `src/package` установлен как пакет. Альтернатива ini —
`[tool.pytest.ini_options]` в `pyproject.toml`; не поддерживай расходящиеся копии конфигурации.
В `norecursedirs` при необходимости добавляй build-каталоги, но не прячь нужные тесты.

Marker можно зарегистрировать также через `config.addinivalue_line("markers", "slow: ...")`
в hook `pytest_configure`; для обычного проекта статическая конфигурация проще.

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

Это отдельные примеры механизмов, не основной исполняемый комплект. `xfail(strict=True)` превращает
неожиданное прохождение в ошибку: после исправления убери marker. Skip не доказывает исправность функции.

## Выбор тестов и отладка

Отдельные команды; необязательные debug-флаги могут открыть интерактивный отладчик.

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

`--lf` использует кэш последнего падения; когда записи отсутствуют, по умолчанию могут запускаться все тесты.
`--ff` запускает прежние падения первыми. `--sw` останавливается на падении и сохраняет точку продолжения.
`-s` отключает capture; с xdist захват вывода имеет дополнительные ограничения.
`--pdb` входит в pdb при ошибке, `--trace` — в начале теста; без необходимости отдельный pytest-ipdb не нужен.
`--tb=auto|short|line|no` меняет объём traceback; в CI не скрывай диагностику без причины.

## Плагины и отчёты

| Возможность | Зависимость | Фрагмент команды |
| --- | --- | --- |
| JUnit XML | Встроено в pytest | `python -m pytest --junitxml=report.xml` |
| Покрытие | pytest-cov | `python -m pytest --cov=demo_service --cov-report=term-missing --cov-report=html` |
| Параллельные workers | pytest-xdist | `python -m pytest -n 2` или `-n auto` |
| Asyncio | pytest-asyncio | `python -m pytest --asyncio-mode=strict` |
| `mocker` | pytest-mock | Fixture в тесте |

Установку в существующий uv-проект записывают `uv add --dev pytest pytest-cov pytest-xdist pytest-mock pytest-asyncio`.
`-n auto` по документации xdist выбирает физические ядра; ограничивай процессы ресурсами CI.
Session fixture действует в каждом worker; общую внешнюю БД разделяй по worker или избегай shared state.
Порядок выполнения тестов не должен быть условием корректности; pytest-order нужен только для специально
обоснованных сценариев. Расширения параметризации вроде pytest-cases требуют собственной документации.

JUnit встроен, а JSON-отчёт тестовых результатов требует выбранного плагина, например
[pytest-json-report](https://github.com/numirias/pytest-json-report): `--json-report --json-report-file=report.json`.
Он не равен JSON-отчёту **coverage**. Здесь JSON-плагин не устанавливался и не выполнялся.
Не скрывай все DeprecationWarning; при обоснованной необходимости настрой узкий `filterwarnings`
по категории, сообщению и модулю и укажи причину.

## Что проверено

2026-11-06, macOS, CPython 3.14.7:

- pytest 9.2.0: 13 основных + 4 mock/async сценария в отдельном временном каталоге.
- pytest-mock 3.17.0, pytest-asyncio 1.4.1.post1: подмена адаптера, передача ошибки, async fixture/result.
- pytest-cov 7.1.0: сформирован терминальный отчёт по `demo_service` и HTML.
- pytest-xdist 3.8.0: тот же набор запущен с двумя workers.
- Создан JUnit XML, проверена сборка и выбор тестов.

Production CI, JSON-плагин и Django-стек не выполнялись. Покрытие показывает исполненные строки,
но не доказывает достаточность утверждений; проверяй ошибочные входы и отказ внешнего адаптера.

## Источники

[Конфигурация/API](https://docs.pytest.org/en/stable/reference/reference.html),
[запуск](https://docs.pytest.org/en/stable/how-to/usage.html),
[pytest-cov](https://pytest-cov.readthedocs.io/en/latest/reporting.html),
[xdist](https://pytest-xdist.readthedocs.io/en/stable/distribution.html).
