# Проверить подмену зависимости FastAPI

Откройте страницу, чтобы проверить обработчик без вызова реальной зависимости.
Начните с самостоятельной программы в одном файле.
Для выбора приёма используйте [короткую карточку](testing.md#подмена-зависимости).

| Задача | Приём | Пример |
| --- | --- | --- |
| Впервые проверить исходную функцию и подмену | Создать небольшое приложение и два теста | [Один файл, установка и запуск](#минимальный-самостоятельный-пример) |
| Подробно проверить восстановление | Использовать приложение из рецепта и отдельные тесты | [Подготовка двух файлов](#подготовить-учебную-папку) · [Полный файл тестов](#полный-файл-тестов) |
| Проверить восстановление после ошибки | Сравнить словарь до и после блока | [Тест восстановления](#полный-файл-тестов) · [Ожидаемый результат](#результат-и-границы) |

Уровень: средний; проверка очистки требует понимания контекстных менеджеров Python.
Предпосылки: функции, словари, импорты, `with`, `try`/`finally` и проверки `assert`.
`pytest` находит функции `test_*` и выполняет их как тесты.
`TestClient` вызывает приложение внутри процесса без сетевого сервера.

## Проверенное окружение

| Проверка | Дата и версии |
| --- | --- |
| Сверено с документацией | 2026-11-06: FastAPI 0.162.0, release notes 0.162.0 от 2026-10-23; Starlette TestClient |
| Выполнено | 2026-11-06: Python 3.14.7, FastAPI 0.162.0, Pydantic 2.14.3, Starlette 1.10.0, HTTPX2 2.16.0, pytest 9.2.0; два теста самостоятельной программы и шесть расширенных тестов ниже |

Проверено указанное сочетание версий.
Другие версии не запускались.
Для повторения используйте Python 3.14.7.

## Минимальный самостоятельный пример

**Ситуация:** нужно проверить ответ обработчика, временно пропустив реальную проверку заголовка.
**Предпосылки:** вы умеете определять функции, импортировать модули и работать со словарями.
Понимания `with`, `try`/`finally` и `assert` достаточно для чтения теста.

Зависимость здесь — функция `verify_client`, которая проверяет заголовок до вызова обработчика.
`Depends(verify_client)` объявляет связь между маршрутом и этой функцией.
Обычно FastAPI вызывает исходную функцию; при подмене FastAPI вызывает другую функцию вместо исходной.
`dependency_overrides` — словарь приложения: ключом служит исходный объект функции, значением — функция подмены.
`TestClient` выполняет запрос в приложение внутри процесса, без сетевого сервера.
`pytest` находит функции `test_*`; `assert` проверяет ожидаемый результат.
Блок `finally` выполняет очистку при выходе из `try`, включая выход из-за исключения.
`Header()` задаёт источник параметра `x_client`: заголовок `X-Client`.
`Annotated` связывает тип `str` с этой настройкой.

Создайте отдельную папку `fastapi-override-demo`.
Сохраните полный блок ниже как `test_dependency_override.py` в этой папке.
Этот файл содержит приложение, учебные данные и тесты.

<!-- example: test_dependency_override.py -->
```python
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.testclient import TestClient

app = FastAPI()


def verify_client(x_client: Annotated[str, Header()]):
    if x_client != "training-client":
        raise HTTPException(400, "Неизвестный клиент")


@app.get("/checked", dependencies=[Depends(verify_client)])
def checked():
    return {"checked": True}


def test_real_header_check():
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        assert client.get("/checked", headers={"X-Client": "wrong"}).status_code == 400
        assert client.get("/checked", headers={"X-Client": "training-client"}).status_code == 200


def test_override():
    calls = []

    def skip_client_check():
        calls.append("override")
        return None

    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = skip_client_check
        with TestClient(app) as client:
            response = client.get("/checked")
            assert response.status_code == 200
            assert response.json() == {"checked": True}
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)
    assert calls == ["override"]
    assert app.dependency_overrides == previous
```

Откройте терминал в папке `fastapi-override-demo`.
Используйте Python 3.14.7 для создания отдельного окружения.
Выполните команды оболочки на macOS или Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'
python -m pytest -q test_dependency_override.py
```

**Результат:** `2 passed`.
Первый тест проверяет исходное поведение: без заголовка — `422`, неверный заголовок — `400`, учебный заголовок — `200`.
Второй тест получает `200` и `{"checked": true}` без заголовка.
Запись в `calls` подтверждает вызов подмены, а сравнение словаря подтверждает восстановление прежних записей.

**Ограничения:** учебный заголовок не является аутентификацией.
Подмена действует на всё приложение, пока запись остаётся в словаре.
Не изменяйте подмены одновременно для общего `app` внутри одного процесса.
Выход из `TestClient` сам подмены не очищает.
Подмена здесь возвращает `None`, потому что маршрут использует зависимость только как проверку.
Для результата, передаваемого в обработчик, верните подходящее значение.

Сами тесты работают без внешней сети; установка требует доступа к индексу пакетов.
Данные синтетические; секреты и внешние сервисы не используются.
Проверка заранее установленных подмен и ошибки внутри блока находится в [расширенном сценарии](#полный-файл-тестов).
Дополнительные ограничения подзависимостей и прямых вызовов находятся в [карточке](testing.md#подмена-зависимости).

## Подготовить учебную папку

Для расширенной проверки подготовьте приложение и тесты в двух файлах.
Создайте отдельную учебную папку.
Сохраните [полный исходный файл `header_dependency.py`](recipes.md#проверка-заголовка-перед-обработчиком) в эту папку.
Сохраните следующий блок как `test_dependencies.py` рядом с приложением.
Другие приложения из раздела FastAPI не нужны.
Данные синтетические; секреты и внешние сервисы не используются.

Выполните команды оболочки из учебной папки:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'fastapi==0.162.0' 'httpx2==2.16.0' 'pytest==9.2.0'
python -m pytest -q test_dependencies.py
```

Установка требует доступа к индексу пакетов.
Сами тесты работают без внешней сети.
Starlette использует HTTPX2 для `TestClient`.

## Полный файл тестов

Полный файл `test_dependencies.py` использует только `header_dependency.py` из подготовки.
Фикстура — функция подготовки и очистки теста.
`autouse=True` применяет фикстуру ко всем тестам этого файла.
Фикстура временно убирает прежние подмены, чтобы первый тест проверял исходную функцию.

Помощник `overridden_client` ограничивает время действия подмены блоком `with`.
Декоратор `@contextmanager` превращает функцию с `yield` в контекстный менеджер.
Код до `yield` готовит клиент, а `finally` восстанавливает словарь при выходе из блока.
Сам `TestClient` подмены не очищает.

<!-- example: test_dependencies.py -->
```python
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from header_dependency import app, verify_client


@pytest.fixture(autouse=True)
def isolated_overrides():
    previous = app.dependency_overrides.copy()
    app.dependency_overrides.clear()
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


@contextmanager
def overridden_client(replacement):
    previous = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[verify_client] = replacement
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


def test_real_header_check():
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422
        denied = client.get("/checked", headers={"X-Client": "wrong"})
        assert denied.status_code == 400
        assert denied.json() == {"detail": "Неизвестный клиент"}
        allowed = client.get("/checked", headers={"X-Client": "training-client"})
        assert allowed.status_code == 200
        assert allowed.json() == {"checked": True}


def test_override_is_called():
    calls = []

    def skip_client_check():
        calls.append("override")
        return None

    with overridden_client(skip_client_check) as client:
        response = client.get("/checked")
        assert response.status_code == 200
        assert response.json() == {"checked": True}
    assert calls == ["override"]
    assert app.dependency_overrides == {}
    with TestClient(app) as client:
        assert client.get("/checked").status_code == 422


@pytest.mark.parametrize("has_previous", [False, True])
@pytest.mark.parametrize("fail_inside", [False, True])
def test_restores_previous_overrides(has_previous, fail_inside):
    def other_dependency():
        return "unused"

    def previous_check():
        return None

    def previous_other():
        return "previous"

    def replacement():
        return None

    if has_previous:
        app.dependency_overrides.update({
            verify_client: previous_check,
            other_dependency: previous_other,
        })
    previous = app.dependency_overrides.copy()

    def exercise():
        with overridden_client(replacement) as client:
            assert app.dependency_overrides[verify_client] is replacement
            assert client.get("/checked").status_code == 200
            if fail_inside:
                raise AssertionError("Ошибка внутри проверяемого блока")

    if fail_inside:
        with pytest.raises(AssertionError, match="Ошибка внутри проверяемого блока"):
            exercise()
    else:
        exercise()
    assert app.dependency_overrides == previous
```

## Результат и границы

Ожидаемый результат запуска: `6 passed`.
Два первых теста проверяют исходную функцию и вызов подмены.
Параметризация запускает тест восстановления четыре раза: с прежними записями и без них, с исключением и без исключения.
Проверка после `pytest.raises` подтверждает восстановление до завершения теста и очистки фикстуры.
Прежняя запись для `verify_client` возвращается вместе с посторонней записью.

`None` подходит здесь: декоратор маршрута использует зависимость только как проверку.
Для зависимости, которая возвращает пользователя или сессию БД в обработчик, подберите подходящее возвращаемое значение.
[Карточка](testing.md#подмена-зависимости) описывает ключ словаря, подзависимости и область действия подмены.

- [ ] Проверьте исходный отказ без заголовка: `422`.
- [ ] Проверьте отказ с неверным заголовком: `400`.
- [ ] Проверьте успех с учебным заголовком: `200`.
- [ ] Проверьте вызов подмены и успех без заголовка.
- [ ] Проверьте восстановление пустого словаря.
- [ ] Проверьте восстановление прежних записей после обычного выхода.
- [ ] Проверьте восстановление прежних записей после исключения.

Сценарий не проверяет конкурентное изменение общего `app`, зависимости с `yield` или работу внешнего провайдера.
Проверки используют синхронный `TestClient`; async-клиент разобран [отдельно](testing.md#асинхронный-клиент).
Не запускайте эти тесты одновременно с другими тестами того же `app` внутри одного процесса.

## Источники

- [FastAPI: подмена зависимостей](https://fastapi.tiangolo.com/advanced/testing-dependencies/).
- [FastAPI: зависимости в декораторе](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/).
- [FastAPI 0.162.0: разрешение зависимостей](https://github.com/fastapi/fastapi/blob/0.162.0/fastapi/dependencies/utils.py).
- [FastAPI: release notes 0.162.0](https://fastapi.tiangolo.com/release-notes/#01620-2026-10-23).
- [Starlette: TestClient](https://starlette.dev/testclient/).

[Карточка подмены](testing.md#подмена-зависимости) · [Справочник FastAPI](README.md) · [Указатель задач](../../../tasks/README.md#http-api-и-веб-приложения)
