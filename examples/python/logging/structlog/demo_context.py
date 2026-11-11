import asyncio

import structlog
from structlog.contextvars import bound_contextvars, clear_contextvars


async def process_item(item_id):
    with bound_contextvars(item_id=item_id):
        log = structlog.get_logger()
        await log.ainfo("item_started")
        await asyncio.sleep(0)
        await log.ainfo("item_completed")


async def run_tasks():
    clear_contextvars()
    try:
        with bound_contextvars(request_id="training-request"):
            await asyncio.gather(process_item(1), process_item(2))
        structlog.get_logger().info("outside")
    finally:
        clear_contextvars()
