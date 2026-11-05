# Structlog Cheat Sheet

## Содержание

- [Введение](#введение)
- [Быстрый старт](#быстрый-старт)
- [Основные концепции](#основные-концепции)
- [Конфигурация](#конфигурация)
- [Процессоры](#процессоры)
- [Биндеры (биндинг контекста)](#биндеры-биндинг-контекста)
- [Логирование событий и исключений](#логирование-событий-и-исключений)
- [Интеграция со стандартным logging](#интеграция-со-стандартным-logging)
- [Форматирование вывода](#форматирование-вывода)
- [Работа с контекстом](#работа-с-контекстом)
- [Асинхронное использование](#асинхронное-использование)
- [Интеграция с веб-фреймворками](#интеграция-с-веб-фреймворками)
- [Производительность](#производительность)
- [Антипаттерны](#антипаттерны)
- [Полезные ссылки](#полезные-ссылки)

---

## Введение

**Structlog** — современная библиотека для структурированного логирования в Python. В отличие от стандартного модуля `logging`, structlog фокусируется на структурированных данных, а не на форматированных строках.

**Преимущества:**
- Структурированные логи (JSON, Key-Value)
- Высокая производительность
- Гибкая конфигурация через процессоры
- Удобная работа с контекстом
- Отличная поддержка асинхронности

## Быстрый старт

### Установка

```bash
pip install structlog
```

### Минимальный пример

```python
import structlog

logger = structlog.get_logger()
logger.info("Событие произошло", user_id=123, action="login")
```

### Пример с конфигурацией

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)

logger = structlog.get_logger()
logger.info("user_logged_in", user="john_doe", ip="192.168.1.1")
```

## Основные концепции

### 1. **Бандеролы (Bound Logger)**
Логгер с привязанным контекстом. Каждый вызов добавляет контекст к логгеру.

```python
log = logger.bind(user_id=123)
log.info("user_action", action="view")  # В логах будет user_id=123
```

### 2. **Процессоры**
Функции, которые обрабатывают словарь с данными лога по цепочке.

### 3. **Контекстные переменные**
Хранят контекст, который автоматически добавляется ко всем логам.

## Конфигурация

### Базовая конфигурация

```python
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### Конфигурация для разработки

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True)  # Цветной вывод
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
)
```

### Конфигурация для продакшена (JSON)

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
```

## Процессоры

### Встроенные процессоры

| Процессор | Назначение |
|-----------|------------|
| `TimeStamper` | Добавляет временную метку |
| `add_log_level` | Добавляет уровень логирования |
| `JSONRenderer` | Форматирует в JSON |
| `KeyValueRenderer` | Форматирует в key=value |
| `format_exc_info` | Форматирует исключения |
| `StackInfoRenderer` | Добавляет информацию о стеке |
| `UnicodeDecoder` | Декодирует байты в строки |
| `CallsiteParameterAdder` | Добавляет информацию о месте вызова |

### Создание кастомного процессора

```python
def add_service_name(logger, method_name, event_dict):
    event_dict["service"] = "my_service"
    return event_dict

def filter_secrets(logger, method_name, event_dict):
    if "password" in event_dict:
        event_dict["password"] = "***"
    return event_dict

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        add_service_name,
        filter_secrets,
        structlog.processors.JSONRenderer()
    ]
)
```

### Порядок процессоров

```python
processors=[
    # 1. Подготовка (в начале цепочки)
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    
    # 2. Добавление метаданных
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.CallsiteParameterAdder(
        {
            structlog.processors.CallsiteParameter.FILENAME,
            structlog.processors.CallsiteParameter.FUNC_NAME,
            structlog.processors.CallsiteParameter.LINENO,
        }
    ),
    
    # 3. Обработка исключений и стека
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    
    # 4. Фильтрация и трансформация (кастомные процессоры)
    
    # 5. Рендеринг (в конце цепочки)
    structlog.processors.JSONRenderer()
]
```

## Биндеры (биндинг контекста)

### Базовый биндинг

```python
logger = structlog.get_logger()

# Биндинг временного контекста
log = logger.bind(user_id=123, session_id="abc")
log.info("action_performed", action="click")  # Содержит user_id и session_id

# Цепочка биндингов
logger.bind(x=1).bind(y=2).info("test")  # x=1, y=2
```

### Временный биндинг

```python
with logger.bind(trace_id="trace-123"):
    logger.info("inside_context")  # Содержит trace_id
logger.info("outside_context")  # Не содержит trace_id
```

### Unbind (удаление ключей)

```python
log = logger.bind(x=1, y=2, z=3)
log = log.unbind("x", "y")
log.info("test")  # Только z=3
```

## Логирование событий и исключений

### Базовое логирование

```python
logger.debug("debug_message", data="value")
logger.info("user_login", username="john", ip="192.168.1.1")
logger.warning("slow_query", duration=2.5, query="SELECT * FROM users")
logger.error("db_connection_failed", db="primary", error="timeout")
logger.critical("system_failure", component="database")
```

### Логирование исключений

```python
try:
    risky_operation()
except Exception as e:
    logger.exception("operation_failed", 
                     user_id=123, 
                     operation="import_data",
                     error=str(e))
    # Или альтернативно:
    logger.error("operation_failed", 
                 exc_info=True, 
                 user_id=123,
                 operation="import_data")
```

### Try/except с контекстом

```python
def process_user(user_id):
    logger = structlog.get_logger().bind(user_id=user_id)
    
    try:
        logger.info("processing_started")
        # ... код ...
        logger.info("processing_completed")
    except Exception:
        logger.exception("processing_failed")
        raise
```

## Интеграция со стандартным logging

### Использование ProcessorFormatter

```python
import logging
import structlog

# Настройка structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Настройка стандартного logging
formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.JSONRenderer(),
    foreign_pre_chain=[
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ],
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

# Использование
logger = structlog.get_logger()
logger.info("message", key="value")
```

### Получение стандартного логгера

```python
import structlog
import logging

# Получаем stdlib logger через structlog
logger = structlog.get_logger("my_module")
# или
logger = structlog.wrap_logger(
    logging.getLogger("my_module")
)
```

## Форматирование вывода

### Консольный вывод (для разработки)

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True)
    ]
)
```

### JSON вывод (для продакшена)

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(
            # Опции сериализации
            serializer=lambda obj, **kwargs: str(obj)
        )
    ]
)
```

### Key-Value вывод

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.KeyValueRenderer(
            key_order=["timestamp", "level", "event"],
            drop_missing=True
        )
    ]
)
```

### Кастомный рендерер

```python
def custom_renderer(logger, method_name, event_dict):
    return f"{event_dict.get('timestamp')} | {event_dict.get('level')} | {event_dict.get('event')}"

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        custom_renderer
    ]
)
```

## Работа с контекстом

### ContextVars (асинхронно-безопасный контекст)

```python
import structlog
from structlog import contextvars

# Установка контекстных переменных
contextvars.bind_contextvars(
    request_id="req-123",
    user_id=456
)

logger = structlog.get_logger()
logger.info("processing")  # Автоматически включает request_id и user_id

# Очистка контекста
contextvars.clear_contextvars()

# Временный контекст
with contextvars.bound_contextvars(temp="value"):
    logger.info("inside")  # Содержит temp="value"
```

### Thread-local контекст (устаревший способ)

```python
import structlog
from structlog import threadlocal

# Биндинг
threadlocal.bind_threadlocal(
    request_id="req-123",
    user_id=456
)

# Временный биндинг
with threadlocal.tmp_bind_threadlocal(temp="value"):
    logger.info("message")

# Очистка
threadlocal.clear_threadlocal()
```

## Асинхронное использование

### Базовая настройка для async/await

```python
import structlog
import asyncio

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,  # Важно для async!
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

async def task():
    logger = structlog.get_logger()
    logger.info("async_task_started")
    await asyncio.sleep(0.1)
    logger.info("async_task_completed")

asyncio.run(task())
```

### Контекст в асинхронных задачах

```python
import asyncio
import structlog
from structlog import contextvars

async def process_item(item_id):
    # Устанавливаем контекст для этой задачи
    contextvars.bind_contextvars(item_id=item_id)
    
    logger = structlog.get_logger()
    logger.info("processing_item")
    
    # Контекст автоматически передается
    await asyncio.sleep(0.1)
    logger.info("item_processed")
    
    # Очищаем контекст
    contextvars.clear_contextvars()

async def main():
    tasks = [process_item(i) for i in range(3)]
    await asyncio.gather(*tasks)
```

## Интеграция с веб-фреймворками

### FastAPI middleware

```python
import uuid
from fastapi import FastAPI, Request
import structlog
from structlog import contextvars

app = FastAPI()
logger = structlog.get_logger()

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    
    # Устанавливаем контекст для запроса
    contextvars.bind_contextvars(
        request_id=request_id,
        path=request.url.path,
        method=request.method
    )
    
    logger.info("request_started")
    
    try:
        response = await call_next(request)
        
        # Добавляем статус код в контекст после выполнения
        contextvars.bind_contextvars(status_code=response.status_code)
        logger.info("request_completed")
        
        return response
    except Exception as e:
        logger.exception("request_failed", error=str(e))
        raise
    finally:
        contextvars.clear_contextvars()

@app.get("/")
async def root():
    logger.info("handler_executed")
    return {"message": "Hello"}
```

### Django integration

```python
# settings.py
import structlog

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "myapp": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

# middleware.py
import structlog
from structlog import contextvars

class StructLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        request_id = request.headers.get("X-Request-ID", "unknown")
        
        contextvars.bind_contextvars(
            request_id=request_id,
            user_id=request.user.id if request.user.is_authenticated else None,
            path=request.path,
            method=request.method,
        )
        
        logger = structlog.get_logger()
        logger.info("request_started")
        
        try:
            response = self.get_response(request)
            contextvars.bind_contextvars(status_code=response.status_code)
            logger.info("request_completed")
            return response
        except Exception:
            logger.exception("request_failed")
            raise
        finally:
            contextvars.clear_contextvars()
```

## Производительность

### Включение кэширования

```python
structlog.configure(
    cache_logger_on_first_use=True,  # ✅ Рекомендуется
    # или
    cache_logger_on_first_use=False,  # Только для отладки
)
```

### Оптимизация процессоров

```python
# Быстрые процессоры идут первыми
processors=[
    # Быстрые фильтры
    structlog.processors.add_log_level,
    
    # Медленные процессоры только при необходимости
    structlog.processors.StackInfoRenderer(),  # Только для ERROR+
    structlog.processors.format_exc_info,      # Только при exc_info=True
]
```

### Избегание дорогих вычислений

```python
# ❌ Плохо - вычисляется всегда
logger.info("data", result=expensive_operation())

# ✅ Хорошо - вычисляется только если нужно
logger.info("data", result=structlog.dev.lazy(expensive_operation))

# ✅ Или с проверкой уровня
if logger.isEnabledFor(logging.DEBUG):
    logger.debug("debug_data", data=expensive_operation())
```

## Антипаттерны

### 1. **Использование f-строк в сообщениях**

```python
# ❌ Плохо - теряется структура
logger.info(f"User {user_id} logged in from {ip}")

# ✅ Хорошо - структурированные данные
logger.info("user_logged_in", user_id=user_id, ip=ip)
```

### 2. **Избыточный контекст**

```python
# ❌ Плохо - дублирование
logger.bind(user_id=user_id).info("action", user_id=user_id)

# ✅ Хорошо - контекст автоматически добавляется
log = logger.bind(user_id=user_id)
log.info("action")
```

### 3. **Не очистка контекста**

```python
# ❌ Риск утечки контекста
contextvars.bind_contextvars(request_id=req_id)
# ... забыли clear_contextvars()

# ✅ Используйте try/finally или контекстный менеджер
try:
    contextvars.bind_contextvars(request_id=req_id)
    # логика
finally:
    contextvars.clear_contextvars()
```

### 4. **Смешивание event и key-value**

```python
# ❌ Неоднозначно
logger.info("user login", event="login", user="john")

# ✅ Ясно разделено
logger.info("user_login", user="john")  # event="user_login"
```

### 5. **Игнорирование исключений**

```python
# ❌ Теряется стектрейс
try:
    risky()
except Exception as e:
    logger.error(f"Failed: {e}")  # Нет exc_info!

# ✅ Сохраняем стектрейс
try:
    risky()
except Exception:
    logger.exception("operation_failed")
    # или
    logger.error("operation_failed", exc_info=True)
```

## Полезные ссылки

- [Официальная документация](https://www.structlog.org/)
- [GitHub репозиторий](https://github.com/hynek/structlog)
- [Статья "Structured Logging in Python"](https://hynek.me/articles/structured-logging/)
- [Примеры конфигураций](https://www.structlog.org/en/stable/configuration.html)
- [Best Practices](https://www.structlog.org/en/stable/best-practices.html)

---

## Шпаргалка для копирования

### Базовая конфигурация (JSON)

```python
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
```

### Конфигурация для разработки

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="%H:%M:%S"),
        structlog.dev.ConsoleRenderer(colors=True)
    ]
)
```

### FastAPI middleware (минимум)

```python
@app.middleware("http")
async def add_logging(request: Request, call_next):
    contextvars.bind_contextvars(request_id=str(uuid.uuid4()))
    try:
        return await call_next(request)
    finally:
        contextvars.clear_contextvars()
```

---

*Этот cheat sheet охватывает основные аспекты работы с structlog. Библиотека активно развивается, поэтому для самых актуальных деталей всегда проверяйте официальную документацию.*
