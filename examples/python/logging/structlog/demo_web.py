from uuid import uuid4

import structlog
from fastapi import FastAPI
from starlette.types import ASGIApp, Receive, Scope, Send
from structlog.contextvars import bind_contextvars, clear_contextvars


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        clear_contextvars()
        request_id = uuid4().hex
        bind_contextvars(request_id=request_id, method=scope["method"], path=scope["path"])
        log = structlog.get_logger()
        log.info("request_started")

        async def send_with_id(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii")))
                message = {**message, "headers": headers}
                log.info("response_started", status_code=message["status"])
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
            log.info("request_completed")
        except Exception:
            log.exception("request_failed")
            raise
        finally:
            clear_contextvars()


app = FastAPI()
app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
async def root():
    structlog.get_logger().info("handler_executed")
    return {"ok": True}


@app.get("/fail")
async def fail():
    raise RuntimeError("training failure")
