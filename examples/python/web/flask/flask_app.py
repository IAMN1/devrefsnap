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
