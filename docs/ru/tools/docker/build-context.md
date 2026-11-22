# Собрать main.py из корня с Dockerfile в dockers/

[English](../../../en/tools/docker/build-context.md)

Если `main.py` лежит в корне проекта, а Dockerfile — в `dockers/`, выберите корень проекта контекстом сборки. Тогда `COPY main.py .` найдёт исходный файл. Дерево показывает два возможных места для `compose.yaml`. Для запуска достаточно одного файла Compose. Для сборки нужен работающий Docker и образ `python:3.14-slim`. При первой сборке Docker скачает образ с Docker Hub, если его ещё нет на компьютере. Для команд `docker compose` понадобится также Compose.

```text
docker-build-context/
├── .dockerignore
├── main.py
├── compose.yaml
└── dockers/
    ├── Dockerfile
    └── compose.yaml
```

[main.py](../../../../examples/tools/docker-build-context/main.py) выводит свой полный путь. Так вы увидите, куда Docker скопировал программу.

```python
from pathlib import Path

print(Path(__file__).resolve())
```

## Куда положить .dockerignore

Положите [`.dockerignore`](../../../../examples/tools/docker-build-context/.dockerignore) в корень контекста сборки, рядом с `main.py`. Для обеих раскладок Compose это каталог `docker-build-context/`. Исключите из контекста локальное окружение Python, данные Git и файл настроек.

```text
.venv
.git
.env
```

Каждая строка исключает одно имя в корне контекста. Сборщик по-прежнему может скопировать `main.py`. Compose может читать локальный `.env` для подстановки переменных в YAML.

Если понадобятся отдельные правила только для этого Dockerfile, используйте `dockers/Dockerfile.dockerignore`. При сборке этого файла Docker отдаст им приоритет перед корневым списком. [Правила Docker](https://docs.docker.com/build/concepts/context/#dockerignore-files).

## Каталог запуска

Перейдите из корня репозитория в каталог примера.

```bash
cd examples/tools/docker-build-context
```

## Собрать образ

**Один Dockerfile для обоих вариантов.** [dockers/Dockerfile](../../../../examples/tools/docker-build-context/dockers/Dockerfile)

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY main.py .
CMD ["python", "main.py"]
```

**Сборка без Compose.** Выполните команды из корня примера (`examples/tools/docker-build-context/`). Параметр `-f` указывает путь к Dockerfile от текущего каталога терминала. Последняя точка выбирает этот каталог контекстом сборки.

```bash
docker build -f dockers/Dockerfile -t devrefsnap-context:local .
docker run --rm devrefsnap-context:local
```

В `COPY main.py .` источник `main.py` отсчитывается от корня контекста. Если контекстом выбрать только `dockers/`, файл окажется за его пределами. Точка справа означает рабочий каталог внутри образа. Его задаёт `WORKDIR /app`, поэтому [программа](../../../../examples/tools/docker-build-context/main.py) выводит `/app/main.py`.

## compose.yaml в корне

[compose.yaml в корне](../../../../examples/tools/docker-build-context/compose.yaml). Точка в `context` выбирает каталог, в котором лежит `main.py`.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: dockers/Dockerfile
```

## compose.yaml в dockers/

[compose.yaml в dockers/](../../../../examples/tools/docker-build-context/dockers/compose.yaml). Значение `..` поднимает контекст на один уровень от каталога Compose-файла, к `main.py`.

```yaml
services:
  app:
    build:
      context: ..
      dockerfile: dockers/Dockerfile
```

В обоих вариантах Compose отсчитывает `dockerfile` от выбранного контекста. Контекст в обоих случаях — корень проекта, поэтому путь остаётся `dockers/Dockerfile`. Из корня примера выберите одну команду. Ожидаемый вывод приложения — `/app/main.py`.

| Расположение файла | Сборка и разовый запуск |
| --- | --- |
| `compose.yaml` | `docker compose -f compose.yaml run --rm --build app` |
| `dockers/compose.yaml` | `docker compose -f dockers/compose.yaml run --rm --build app` |

[Поля compose.yaml](compose-file.md) · [Инструкции Dockerfile](dockerfile.md)
