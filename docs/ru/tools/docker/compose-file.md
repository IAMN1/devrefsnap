# Шпаргалка по полям compose.yaml

[English](../../../en/tools/docker/compose-file.md)

В `services` описывают сервисы. Верхние разделы `volumes` и `networks` объявляют именованные ресурсы проекта. Чтобы сервис использовал ресурс, его имя указывают ещё раз внутри сервиса. [Полный файл для трёх сервисов](lab.md#composeyaml) · [Методичка со схемой](guide.md).

## Описать сервис

| Что нужно указать | Запись в сервисе | Что она означает |
| --- | --- | --- |
| Собственный образ | `build: .` | Собрать образ по Dockerfile из каталога с Compose-файлом |
| Готовый образ | `image: nginx:stable-alpine` | Взять образ Nginx с указанным тегом |
| Рабочий каталог | `working_dir: /site/catalog` | Из этого каталога стартует процесс |
| Порт на компьютере | `ports: ["127.0.0.1:18083:80"]` | Запрос на локальный порт 18083 попадёт на порт 80 контейнера |
| Участие в сети | `networks: [catalog-net]` | Сервисы этой сети могут найти друг друга по имени |
| Место для данных | `volumes: ["catalog-pages:/site/catalog"]` | Подключить именованный том по пути внутри контейнера |

Compose использует современную спецификацию без верхнего поля `version`. При совместном использовании `build` и `image` выбор загрузки или сборки зависит от `pull_policy`. [Спецификация Compose](https://docs.docker.com/reference/compose-file/) · [Правила сборки](https://docs.docker.com/reference/compose-file/build/).

## Указать Dockerfile

В копии репозитория откройте каталог `examples/tools/docker-build-context/`. В нём лежит [main.py](../../../../examples/tools/docker-build-context/main.py). Соберите образ из этого каталога.

```bash
docker build -f dockers/Dockerfile -t devrefsnap-context:local .
```

| Файл Compose | `build.context` | `build.dockerfile` |
| --- | --- | --- |
| [В корне](../../../../examples/tools/docker-build-context/compose.yaml) | `.` | `dockers/Dockerfile` |
| [В dockers/](../../../../examples/tools/docker-build-context/dockers/compose.yaml) | `..` | `dockers/Dockerfile` |

Эти два примера запускаются по отдельности. Для одного Compose-файла с обычными параметрами Compose отсчитывает `context` от каталога файла, а `dockerfile` — от контекста. В обоих случаях `COPY main.py .` берёт файл из корня проекта.

### Куда положить .dockerignore

Положите [`.dockerignore`](../../../../examples/tools/docker-build-context/.dockerignore) рядом с `main.py`, в корень контекста сборки. Каждая строка исключает одно имя в этом корне.

```text
.venv
.git
.env
```

[Дерево, полные файлы и команды запуска обоих вариантов](build-context.md) · [Как Docker читает .dockerignore](https://docs.docker.com/build/concepts/context/#dockerignore-files).

Для выбора именованной стадии добавьте `target` под `build`. [Пример с двумя стадиями](../../../../examples/tools/api-contract-lab/compose.yaml) · [Пути сборки в Compose](https://docs.docker.com/reference/compose-file/build/).

## Передать настройки

| Кому нужно значение | Где его задать | Пример |
| --- | --- | --- |
| Compose при чтении YAML | В оболочке или в файле `.env` текущего каталога запуска. Путь к другому файлу задаёт `--env-file` | `${SITE_PORT:-18083}` выбирает 18083, если значение пустое или отсутствует. В этом примере значение из оболочки имеет приоритет. |
| Процессу внутри контейнера | В `environment` сервиса | `environment: {LOG_LEVEL: info}` передаёт `LOG_LEVEL=info` программе |
| Процессу нужны значения из файла | В `env_file` сервиса | `env_file: ./app.env` передаёт пары `KEY=value`. При совпадении имён приоритет у `environment`. |

Из корня репозитория выполните `SITE_PORT=18084 docker compose -f examples/tools/compose-site/compose.yaml config`. В разделе `services.gateway.ports` поле `published` получит значение `18084`. [Compose-файл этого примера](../../../../examples/tools/compose-site/compose.yaml). Вывод может содержать значения паролей. Флаг `-q` проверяет конфигурацию без вывода значений. [Подстановка в YAML](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Переменные контейнера](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Подключить базу данных

На общей сети приложение обращается к PostgreSQL по имени сервиса, например `postgres:5432`. Для этого публиковать порт БД на компьютере не нужно. Запись `depends_on: [postgres]` задаёт порядок старта. Если приложению нужна готовая база, укажите `depends_on.postgres.condition: service_healthy` и задайте `healthcheck` у БД. Повторным подключением после сбоя управляет приложение. [Полный пример с PostgreSQL](../../../../examples/tools/compose-and-github-actions/compose.yaml) · [Готовность зависимостей](https://docs.docker.com/compose/how-tos/startup-order/).

## Выбрать хранилище

| Задача | Запись внутри списка `volumes` | Результат |
| --- | --- | --- |
| Сохранить файлы при замене контейнера | `catalog-pages:/site/catalog` | Именованный том сохраняет данные. Обычный `down` его оставляет. |
| Подключить свой файл настроек | `./gateway.conf:/etc/nginx/conf.d/default.conf:ro` | Контейнер читает файл с компьютера. Суффикс `ro` запрещает запись через эту привязку. |

При подключении тома его содержимое видно вместо файлов образа по тому же пути. Пустой том по умолчанию получает начальные файлы из образа. Команда `docker compose down -v` удаляет управляемые тома проекта с данными. Внешние тома с `external: true` сохраняются. [Тома Docker](https://docs.docker.com/engine/storage/volumes/) · [Привязка файлов](https://docs.docker.com/engine/storage/bind-mounts/).

[Все материалы по Docker](README.md)
