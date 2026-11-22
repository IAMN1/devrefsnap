
# Создать HTTP API с проверкой данных

[English](../../../../en/python/web/fastapi/http-api.md)

Откройте страницу, чтобы выполнить полный CRUD и проверить согласованность входной и выходной модели.
Учебные товары хранятся в памяти одного процесса.

| Задача | Приём | Пример |
| --- | --- | --- |
| Повторить CRUD | Path/query/body, модели, управляемые ошибки | [Полный main.py](#http-api-с-валидацией) |
| Понять изменение PATCH | Объединить поля и повторно проверить модель | [Короткая карточка](recipes.md#http-api-с-валидацией) |
| Проверить ошибки и пароль | `TestClient` и независимые ожидаемые значения | [Полные тесты](testing-lab.md#синхронный-testclient) |

[Карточки HTTP](recipes.md) · [Справочник FastAPI](README.md) · [Проверки](testing.md)

Уровень: базовый → средний.
Для запуска нужны Python 3.14, FastAPI 0.165.0 и Pydantic 2.14.4.


## HTTP API с валидацией

**Предпосылки:** функции, типы, HTTP-методы.

В отдельном окружении выполните `python -m pip install 'fastapi==0.165.0' 'uvicorn[standard]==0.54.0' 'pydantic[email]==2.14.4'`.
Создайте полный файл `main.py`:

[`main.py`](../../../../../examples/python/web/fastapi/main.py)

Запуск и запросы в другом терминале:

```bash
uvicorn main:app --reload
```

```bash
curl -i -X POST http://127.0.0.1:8000/items -H 'Content-Type: application/json' -d '{"name":"Book","price":25,"tags":["python"]}'
curl 'http://127.0.0.1:8000/items?q=Book&tags=python&limit=5'
curl -i -X PATCH http://127.0.0.1:8000/items/1 -H 'Content-Type: application/json' -d '{"price":30}'
curl -i http://127.0.0.1:8000/items/999
```

Чтобы прочитать статус, заголовки и JSON из ответа, используйте [пример с `curl` и `jq`](../../../tools/http-json.md#посмотреть-http-ответ).

Результат создания — `201` с `id=1`.
Выборка возвращает список из одного товара.
PATCH меняет цену на `30`.
Запрос отсутствующего товара даёт `404`.
Отрицательная цена и `premium` дешевле `100` дают `422`.
`DELETE` возвращает `204` без тела.
Маршрут `/user-preview` демонстрирует фильтрацию пароля выходной моделью.
Маршрут не сохраняет пользователя и не является регистрацией.

Ограничения: данные живут до перезапуска в одном процессе.
Это хранилище не обеспечивает постоянство данных и конкурентный доступ.
Здесь `float` выбран для простоты.
Для точных денежных расчётов нужна отдельно выбранная модель чисел.
PATCH сначала объединяет поля.
Затем PATCH повторно проверяет всю модель.
Сам по себе `model_copy(update=...)` не выполняет такую валидацию.
Явный `null` допускается только у полей итоговой модели, допускающих `None`.

Цена и налог должны быть конечными числами.
`allow_inf_nan=False` отклоняет бесконечность и NaN.
Число `1e999` может стать `inf` уже при разборе JSON.
Поэтому обработчик ошибки возвращает только `loc`, `msg`, `type`.
Обработчик исключает исходный `input` и `ctx`.
Эти значения сами могут не сериализоваться в JSON.
Тот же формат используется при повторной валидации PATCH.

Источники: [ограничения параметров](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/), [Pydantic v2 validators](https://pydantic.dev/docs/validation/latest/concepts/validators/), [ограничения Field](https://pydantic.dev/docs/validation/latest/api/pydantic/fields/#pydantic.fields.Field), [обновление body](https://fastapi.tiangolo.com/tutorial/body-updates/), [выходная модель](https://fastapi.tiangolo.com/tutorial/response-model/), [обработка ошибок](https://fastapi.tiangolo.com/tutorial/handling-errors/).
