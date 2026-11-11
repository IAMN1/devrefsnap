import logging

import structlog

from demo_logging import redact, service


def configure_stdlib(stream):
    shared = [structlog.contextvars.merge_contextvars, structlog.stdlib.add_log_level,
              structlog.stdlib.add_logger_name, structlog.processors.TimeStamper(fmt="iso"), service]
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processors=[structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                    structlog.processors.format_exc_info, redact, structlog.processors.JSONRenderer()],
    )
    handler = logging.StreamHandler(stream)
    handler.setFormatter(formatter)
    logger = logging.getLogger("training")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    structlog.configure(
        processors=[structlog.stdlib.filter_by_level, *shared,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter],
        context_class=dict, logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger, cache_logger_on_first_use=True,
    )
    return structlog.get_logger("training.structured"), logging.getLogger("training.plain")
