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

Фрагмент описания сервиса, если файл сборки находится в `site/docker/Dockerfile`.

```yaml
build:
  context: ./site
  dockerfile: docker/Dockerfile
```

Для одного Compose-файла путь `context` отсчитывается от его каталога. Путь `dockerfile` отсчитывается от контекста. При таком выборе инструкция `COPY message.txt ./` читает `site/message.txt`. Для выбора именованной стадии добавьте `target` под `build`. [Пример с двумя стадиями](../../../../examples/tools/api-contract-lab/compose.yaml).

## Передать настройки

| Кому нужно значение | Где его задать | Пример |
| --- | --- | --- |
| Compose при чтении YAML | В оболочке или в файле `.env` рядом с этим Compose-файлом | `${SITE_PORT:-18083}` выбирает 18083, если значение пустое или отсутствует. В этом примере значение из оболочки имеет приоритет. |
| Процессу внутри контейнера | В `environment` сервиса | `environment: {LOG_LEVEL: info}` передаёт `LOG_LEVEL=info` программе |
| Процессу нужны значения из файла | В `env_file` сервиса | `env_file: ./app.env` передаёт пары `KEY=value`. При совпадении имён приоритет у `environment`. |

Команда `SITE_PORT=18084 docker compose config` покажет итоговый порт. Вывод может содержать значения паролей. Флаг `-q` проверяет конфигурацию без вывода значений. [Подстановка в YAML](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Переменные контейнера](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Подключить базу данных

На общей сети приложение обращается к PostgreSQL по имени сервиса, например `postgres:5432`. Для этого публиковать порт БД на компьютере не нужно. Запись `depends_on: [postgres]` задаёт порядок старта. Если приложению нужна готовая база, укажите `depends_on.postgres.condition: service_healthy` и задайте `healthcheck` у БД. Повторным подключением после сбоя управляет приложение. [Полный пример с PostgreSQL](../../../../examples/tools/compose-and-github-actions/compose.yaml) · [Готовность зависимостей](https://docs.docker.com/compose/how-tos/startup-order/).

## Выбрать хранилище

| Задача | Запись внутри списка `volumes` | Результат |
| --- | --- | --- |
| Сохранить файлы при замене контейнера | `catalog-pages:/site/catalog` | Именованный том сохраняет данные. Обычный `down` его оставляет. |
| Подключить свой файл настроек | `./gateway.conf:/etc/nginx/conf.d/default.conf:ro` | Контейнер читает файл с компьютера. Суффикс `ro` запрещает запись через эту привязку. |

При подключении тома его содержимое видно вместо файлов образа по тому же пути. Пустой том по умолчанию получает начальные файлы из образа. Команда `docker compose down -v` удаляет управляемые тома проекта с данными. Внешние тома с `external: true` сохраняются. [Тома Docker](https://docs.docker.com/engine/storage/volumes/) · [Привязка файлов](https://docs.docker.com/engine/storage/bind-mounts/).

[Все материалы по Docker](README.md)
