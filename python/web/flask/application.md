# Factory, Blueprint, запрос и ответ Flask

Уровень: базовый и средний. Предпосылки: Flask 3.1.x и Python.
[К справочнику Flask](README.md).

## Полное приложение

Сохраните полный пример как `flask_app.py` в отдельном учебном каталоге.
Пример намеренно не использует хранилище.
Маршрут item показывает один фиксированный ответ.
Маршрут greet преобразует входные данные.
Пример демонстрирует API.
Пример не реализует систему пользователей или механизм аутентификации.

<!-- example: flask/flask_app.py -->
```python
import json

from flask import Blueprint, Flask, abort, jsonify, render_template_string, request
from werkzeug.exceptions import HTTPException

api = Blueprint("api", __name__)


@api.get("/items/<int:item_id>")
def get_item(item_id):
    if item_id != 1:
        abort(404, description="item not found")
    return jsonify(id=1, name="apple")


@api.post("/greet")
def greet():
    payload = request.get_json()
    if not isinstance(payload, dict):
        abort(400, description="JSON object required")
    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        abort(400, description="name must be a non-empty string")
    return jsonify(greeting=f"Hello, {name.strip()}")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(MAX_CONTENT_LENGTH=16 * 1024)
    app.config.from_prefixed_env()
    if test_config is not None:
        app.config.update(test_config)
    app.register_blueprint(api, url_prefix="/api")

    @app.get("/")
    def index():
        return render_template_string(
            "<h1>Hello {{ name }}</h1>", name=request.args.get("name", "reader")
        )

    @app.errorhandler(HTTPException)
    def http_error(error):
        response = error.get_response()
        response.data = json.dumps({"error": error.name, "message": error.description})
        response.content_type = "application/json"
        return response

    return app
```

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
