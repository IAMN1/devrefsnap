# Составить compose.yaml для своего приложения

[English](../../../en/tools/docker/compose-file.md)

Опишите, откуда взять образ каждого сервиса и как запустить его контейнер. Начните с одного HTTP-сервера. Затем посмотрите, какие поля нужны приложению с базой данных.

| Задача | Поля Compose | Пример |
| --- | --- | --- |
| Запустить код из Dockerfile | `services`, `build`, `ports` | [Полный файл для одного сервиса](#описать-сервис) |
| Выбрать другой Dockerfile или стадию | `context`, `dockerfile`, `target` | [Пути сборки](#указать-dockerfile) |
| Поменять порт или настройку процесса | `${…}`, `environment`, `env_file` | [Подстановка и окружение](#передать-настройки) |
| Соединить сервисы по сети | `image`, `depends_on`, `healthcheck` | [Приложение и PostgreSQL](#подключить-базу-данных) |
| Сохранить данные или подставить локальный файл | `volumes` | [Том и привязка файла](#выбрать-хранилище) |

## Описать сервис

Положите `compose.yaml` рядом с [Dockerfile сервера](dockerfile.md#собрать-первый-образ) и `message.txt`. Ниже полный файл для этого проекта. Используйте синтаксис `docker compose` и Compose Specification. Верхнее поле `version` устарело. [Файл примера](../../../../examples/tools/docker-basics/compose.yaml) · [Версия спецификации](https://docs.docker.com/reference/compose-file/version-and-name/).

```yaml
services:
  web:
    build: .
    ports:
      - "127.0.0.1:${SITE_PORT:-18081}:8000"
```

1. Назовите сервис под ключом `services`. Здесь имя `web` можно передать команде `docker compose logs web`. Отступ объединяет настройки этого сервиса.
2. Укажите `build: .`, если хотите собрать свой образ из соседнего Dockerfile. Для готового образа укажите `image`, например `image: postgres:18.6` в сервисе БД.
3. Запишите публикацию порта строкой в формате `"адрес:порт_компьютера:порт_контейнера"`. В примере сервер слушает `0.0.0.0:8000` внутри контейнера. С компьютера запросите `127.0.0.1:18081`. Привязка к `127.0.0.1` ограничивает публикацию интерфейсом обратной петли.

Из каталога примера выполните `docker compose config --services`. Ожидается одна строка `web`. Чтобы увидеть разрешённые пути и порты, выполните `docker compose config`. Для проверки HTTP выполните [первый запуск](README.md#первый-запуск).

## Указать Dockerfile

Для одного файла Compose относительный `context` начинается от каталога `compose.yaml`. Относительный `dockerfile` начинается от `context`. Например, если исходники находятся в `site/`, а рецепт лежит в `site/docker/Dockerfile`, опишите сервис следующим фрагментом.

```yaml
services:
  web:
    build:
      context: ./site
      dockerfile: docker/Dockerfile
```

В таком Dockerfile команда `COPY message.txt ./` читает `site/message.txt`. Для обычного имени `Dockerfile` в корне контекста достаточно краткой записи `build: ./site`.

Если Dockerfile содержит `FROM … AS client`, поле `target: client` внутри `build` выбирает эту стадию как результат сборки. В примере контракта сервисы `app` и `client` собираются из одного файла. При совместном использовании `build` и `image` порядок загрузки и сборки зависит от `pull_policy`. [Dockerfile со стадиями](../../../../examples/tools/api-contract-lab/Dockerfile) · [Сервисы с build.target](../../../../examples/tools/api-contract-lab/compose.yaml) · [Правила сборки Compose](https://docs.docker.com/reference/compose-file/build/).

## Передать настройки

Запустите команду в каталоге `docker-basics`. Она покажет, какой порт получит сервис при заданном значении.

```bash
SITE_PORT=18082 docker compose config
```

Найдите `published: "18082"` и `target: 8000`. Compose подставляет `SITE_PORT` при чтении YAML. Выражение `${SITE_PORT:-18081}` выбирает `18081`, если переменная отсутствует или пуста. Чтобы сохранить выбор между командами, запишите `SITE_PORT=18082` в `.env` рядом с `compose.yaml`. В этом примере значение из оболочки имеет приоритет.

| Кому нужно значение | Куда его поместить | Результат |
| --- | --- | --- |
| Compose при чтении YAML | Оболочка или `.env` | Подстановка в поле `ports`. Чтобы передать значение процессу, укажите его в настройках сервиса. |
| Программе внутри контейнера | `environment: {LOG_LEVEL: info}` в сервисе | Процесс увидит `LOG_LEVEL=info`, если читает эту переменную. |
| Программе нужны переменные из файла | `env_file: ./app.env` в сервисе | Compose передаст пары `KEY=value` из файла в контейнер. Значения из `environment` имеют приоритет. |

После изменения настроек выполните `docker compose up -d`. Если поменялся порт, проверьте его через `docker compose port web 8000`. Вывод `config` может содержать подставленные пароли. Для проверки без вывода значений используйте `config -q`. [Подстановка](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/) · [Окружение контейнера](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

## Подключить базу данных

В отдельном проекте приложение `app` обращается к сервису `postgres`. Следующий фрагмент показывает настройки подключения и проверки готовности. Для запуска используйте [полный compose.yaml](../../../../examples/tools/compose-and-github-actions/compose.yaml). В нём также заданы учебные учётные данные, том и проверка HTTP. [Подготовка и запуск](../compose-and-github-actions.md#запустить-приложение-локально).

```yaml
services:
  app:
    build: .
    environment:
      PGHOST: postgres
    depends_on:
      postgres:
        condition: service_healthy
  postgres:
    image: postgres:18.6
    healthcheck:
      test: ["CMD", "pg_isready", "-h", "127.0.0.1", "-U", "lab", "-d", "compose_lab"]
      interval: 3s
      timeout: 2s
      retries: 10
```

Compose подключает оба сервиса к сети проекта. Приложение находит БД по имени `postgres` и подключается к порту `5432` внутри сети. Публиковать порт БД на компьютере для этого соединения не требуется. Адрес `127.0.0.1` в проверке относится к контейнеру PostgreSQL. В контейнере `app` тот же адрес ведёт к самому приложению.

Краткая запись `depends_on: [postgres]` задаёт порядок запуска. Условие `service_healthy` заставляет Compose дождаться успешной проверки БД при запуске приложения. После запуска обработку обрывов связи обеспечивает приложение. В полном примере команда `docker compose up -d --wait` ждёт состояния `healthy` для обоих сервисов. Для сервиса без проверки готовности достаточно состояния `running`. В полном примере запрос к `/health` выполняет SQL и возвращает имя базы `compose_lab`. [Сеть Compose](https://docs.docker.com/compose/how-tos/networking/) · [Порядок запуска](https://docs.docker.com/compose/how-tos/startup-order/).

## Выбрать хранилище

| Что нужно сохранить | Как подключить | Что произойдёт после пересоздания контейнера |
| --- | --- | --- |
| Данные учебной БД | В сервисе `postgres` подключите `lab-data:/var/lib/postgresql`. Объявите `lab-data:` под верхним ключом `volumes:`. | Новый контейнер проекта получит тот же именованный том. Путь в этом примере рассчитан на образ PostgreSQL 18. |
| Файл с компьютера для разработки | Добавьте `./message.txt:/site/message.txt:ro` в список `volumes` сервиса `web`. Файл должен существовать. | Контейнер читает файл с компьютера. Привязка скрывает копию файла из образа, а `ro` запрещает запись из контейнера. |

Обычный `docker compose down` сохраняет именованный том. Команда `docker compose down -v` удаляет управляемые проектом тома, включая учебные данные в `lab-data`. Используйте её только для намеренного сброса. Внешние тома с `external: true` Compose сохраняет. [Тома Compose](https://docs.docker.com/reference/compose-file/volumes/) · [Привязки файлов](https://docs.docker.com/engine/storage/bind-mounts/) · [Действие down](https://docs.docker.com/reference/cli/docker/compose/down/).

[Команды Compose](commands.md) · [Dockerfile и Docker Compose](README.md)
