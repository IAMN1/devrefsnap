
# Factory, Blueprint, запрос и ответ Flask

[English](../../../../en/python/web/flask/application.md)

Откройте страницу, чтобы создать независимый экземпляр Flask и обработать JSON-запрос.
Полное приложение использует фиксированные учебные данные без БД и аутентификации.

| Задача | Приём | Пример / подробности |
| --- | --- | --- |
| Создать app и подключить маршруты | Factory и Blueprint | [Полный flask_app.py](#полное-приложение) |
| Проверить JSON и вернуть HTTP-ошибку | `request.get_json`, `abort` | [Приложение](#полное-приложение) · [Тесты](testing.md) |
| Запустить локальный сервер | `flask --app ... run --debug` | [Запуск](#запуск-и-проверка) |
| Выбрать форму ответа | Query, HTML, cookie, redirect | [Таблица API](#другие-формы-запроса-и-ответа) |

Уровень: базовый и средний. Предпосылки: Flask 3.1.x и Python.
[К справочнику Flask](README.md).


## Полное приложение

Сохраните полный пример как `flask_app.py` в отдельном учебном каталоге.
Пример намеренно не использует хранилище.
Маршрут item показывает один фиксированный ответ.
Маршрут greet преобразует входные данные.
Пример демонстрирует API.
Пример не реализует систему пользователей или механизм аутентификации.

[`flask/flask_app.py`](../../../../../examples/python/web/flask/flask_app.py)

`GET /api/items/1` возвращает 200 и `{"id":1,"name":"apple"}`.
Неизвестный id даёт 404.
`POST /api/greet` с `{"name":" Alice "}` возвращает 200 и `Hello, Alice`.
Неподходящий media type даёт 415.
Некорректный JSON или пустое имя даёт 400.

HTTPException handler сохраняет исходный response и его заголовки, включая `Allow` у 405.
Не заменяйте все исключения на успешный JSON-ответ.
Неожиданные ошибки должны попадать в логи и давать 500.
Клиент не должен получать трассировку.
Глобальный handler для HTTPException затрагивает также ошибки роутера.
Blueprint-specific 404 handler не перехватит неизвестный URL до выбора Blueprint.


## Запуск и проверка

Фрагменты команд оболочки в каталоге файла:

```bash
python -m flask --app flask_app:create_app routes
python -m flask --app flask_app:create_app run --debug
```

`run --debug` открывает локальный dev-сервер.
Не публикуйте debugger наружу.
После ручного запуска выполните команды в отдельном терминале:

```bash
curl --fail-with-body http://127.0.0.1:5000/api/items/1
curl --fail-with-body -H 'Content-Type: application/json' \
  -d '{"name":"Alice"}' http://127.0.0.1:5000/api/greet
```

Чтобы прочитать статус, заголовки и JSON из ответа, используйте [пример с `curl` и `jq`](../../../tools/http-json.md#посмотреть-http-ответ).

Автоматические проверки — [на следующей странице](testing.md).


## Другие формы запроса и ответа

| Задача | API | Ограничение |
| --- | --- | --- |
| Query string | `request.args.get("page", default=1, type=int)` | При ошибке преобразования вернётся default. Задавайте строгую валидацию отдельно |
| HTML form | `request.form` | Для browser mutation нужна защита CSRF |
| Uploaded file | `request.files` | Ограничьте размер. Не считайте имя/тип от клиента доверенными |
| URL по endpoint | `url_for("api.get_item", item_id=1)` | Нужен подходящий app/request context |
| Redirect | `redirect(url_for(...))` | Не разрешайте произвольный внешний redirect из пользовательского URL |
| HTML | `render_template("page.html", name=name)` | Сохраняйте Jinja autoescape включённым. Не применяйте `safe` к недоверенному тексту |
| JSON | `jsonify(...)` или dict/list | Нужны JSON-сериализуемые значения. Код можно вернуть tuple |
| Cookie/session | `session["key"] = value` | Нужен SECRET_KEY. Cookie подписана, но содержимое доступно клиенту |

Пример использует `render_template_string`, чтобы уместить код в одном файле.
В приложении шаблоны обычно хранят в `templates/`.
Затем приложение загружает шаблоны через `render_template`.
Здесь `templates/` обозначает каталог приложения, а не шаблоны репозитория.


## Источники

[Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/),
[Blueprint](https://flask.palletsprojects.com/en/stable/blueprints/),
[factory](https://flask.palletsprojects.com/en/stable/patterns/appfactories/),
[error handling](https://flask.palletsprojects.com/en/stable/errorhandling/).
