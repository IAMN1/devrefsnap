import logging
import sys

import structlog

SENSITIVE_KEYS = {"password", "token", "api_key"}


def redact_value(value):
    if isinstance(value, dict):
        return {key: "***" if str(key).lower() in SENSITIVE_KEYS else redact_value(item)
                for key, item in value.items()}
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_value(item) for item in value)
    return value


def redact(logger, method_name, event_dict):
    return redact_value(event_dict)


def service(logger, method_name, event_dict):
    event_dict.setdefault("service", "training")
    return event_dict


def configure_logging(stream=None, *, output="json", level=logging.INFO):
    if stream is None:
        stream = sys.stdout
    processors = [structlog.contextvars.merge_contextvars, structlog.processors.add_log_level,
                  structlog.processors.TimeStamper(fmt="iso", utc=True), service,
                  structlog.processors.StackInfoRenderer()]
    if output == "json":
        processors += [structlog.processors.format_exc_info, redact, structlog.processors.JSONRenderer()]
    elif output == "console":
        processors += [redact, structlog.dev.ConsoleRenderer(colors=False)]
    elif output == "keyvalue":
        processors += [structlog.processors.format_exc_info, redact,
                       structlog.processors.KeyValueRenderer(key_order=["timestamp", "level", "event"], drop_missing=True)]
    else:
        raise ValueError("output должен быть json, console или keyvalue")
    structlog.configure(processors=processors, context_class=dict,
                        wrapper_class=structlog.make_filtering_bound_logger(level),
                        logger_factory=structlog.WriteLoggerFactory(file=stream),
                        cache_logger_on_first_use=True)
    return structlog.get_logger()


if __name__ == "__main__":
    log = configure_logging().bind(user_id=123)
    log.info("user_logged_in", credentials={"password": "training-password"})
    try:
        1 / 0
    except ZeroDivisionError:
        log.exception("calculation_failed")
