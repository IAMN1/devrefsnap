import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import psycopg


def database_status():
    with psycopg.connect(connect_timeout=3) as connection:
        row = connection.execute("SELECT current_database()").fetchone()
    return {"status": "ok", "database": row[0]}


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/health":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            status = database_status()
        except psycopg.OperationalError:
            self.log_error("PostgreSQL is unavailable")
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)
            return

        body = json.dumps(status).encode("utf-8") + b"\n"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    with ThreadingHTTPServer(("0.0.0.0", 8000), StatusHandler) as server:
        server.serve_forever()
