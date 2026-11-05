# Запустить API и собрать контейнер

[Краткий справочник](README.md) · [Первое приложение](README.md#первый-запуск)

| Параметр | Значение |
| --- | --- |
| Уровень | Средний: запуск; продвинутый: процессы и контейнер |
| Предпосылки | Виртуальное окружение, терминал; для контейнера — Docker |
| Сверено с документацией | 2026-11-06: FastAPI 0.162.0, Uvicorn deployment и FastAPI Docker |
| Выполнено | 2026-11-06: локальный Uvicorn 0.54.0 с `--reload` и `--workers 2` вернул `200` и ожидаемое приветствие; Python 3.14.7, FastAPI 0.162.0. Docker build/run и Gunicorn не выполнялись |

Все команды выполняются в отдельной учебной папке с `minimal.py` из README темы. Это демонстрация запуска, а не публикация сервиса.

## Разработка и несколько процессов

```bash
uvicorn minimal:app --reload --host 127.0.0.1 --port 8000
```

В другом терминале `curl http://127.0.0.1:8000/` должен вернуть `200` и `{"message":"Привет"}`. `Ctrl+C` останавливает сервер. `--reload` перезапускает его при изменении файлов и нужен в разработке.

Запуск нескольких процессов без reload:

```bash
uvicorn minimal:app --host 127.0.0.1 --port 8000 --workers 2
```

Два workers — выбранное число для примера, не рекомендация по размеру сервера. Каждый процесс имеет собственную память и выполняет собственный lifespan. Поэтому словарь товаров из `main.py` нельзя использовать как общую БД. Для внешнего доступа за прокси/в контейнере укажи `--host 0.0.0.0`; настрой HTTPS и доверие proxy headers в соответствии с окружением. `--reload` и `--workers` не совмещаются.

## Gunicorn как отдельный вариант

Для Linux/Unix, если развёртывание уже использует Gunicorn, установи `gunicorn` и отдельный `uvicorn-worker` в окружение приложения:

```bash
python -m pip install gunicorn uvicorn-worker
gunicorn minimal:app -w 2 -k uvicorn_worker.UvicornWorker -b 127.0.0.1:8000
```

Старый путь `uvicorn.workers.UvicornWorker` устарел. Для простого запуска можно использовать встроенные workers Uvicorn; выбирать Gunicorn только ради этого примера не требуется. [Источник: Uvicorn deployment](https://uvicorn.dev/deployment/).

## Контейнер для минимального приложения

Создай в учебной папке `requirements.txt`. Это минимальный набор для `minimal.py`, а не зависимости всех рецептов:

```text
fastapi==0.162.0
uvicorn==0.54.0
```

Dockerfile:

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY minimal.py .
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "minimal:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t fastapi-training .
docker run --rm -p 127.0.0.1:8000:8000 fastapi-training
```

Команды создают локальный образ и запускают контейнер с портом, доступным только на localhost. Проверь `curl http://127.0.0.1:8000/`; останови контейнер через `Ctrl+C`. `--rm` удалит завершённый контейнер, но образ останется. Публикации в registry здесь нет.

Тег базового образа и версии пакетов нужно обновлять осознанно; этот Dockerfile не является проверкой всех платформ/архитектур. Для воспроизводимого окружения проекта зафиксируй транзитивные зависимости lock-файлом и при необходимости digest образа. В оркестраторе часто запускают один процесс на контейнер и масштабируют контейнеры; это зависит от инфраструктуры.

## Сохранить OpenAPI

Команда импортирует учебное приложение и записывает/перезаписывает `openapi.json` в текущей папке:

```bash
python -c 'import json; from minimal import app; print(json.dumps(app.openapi(), ensure_ascii=False, indent=2))' > openapi.json
```

Либо получи `/openapi.json` у работающего сервера. Генерация схемы не отправляет запросы к маршрутам и не заменяет [поведенческие тесты](testing.md).

## Источники

- [FastAPI: запуск сервера](https://fastapi.tiangolo.com/deployment/manually/), [workers](https://fastapi.tiangolo.com/deployment/server-workers/).
- [FastAPI: контейнеры](https://fastapi.tiangolo.com/deployment/docker/), [HTTPS](https://fastapi.tiangolo.com/deployment/https/).
- [Uvicorn: deployment](https://uvicorn.dev/deployment/), [параметры](https://uvicorn.dev/settings/).
