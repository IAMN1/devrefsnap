# Практикум. Сайт из трёх сервисов

[English](../../../en/tools/docker/lab.md)

Этот сайт доступен через один адрес. Маршрут `/catalog/` открывает каталог, а `/help/` — справку. Ниже приведены оба итоговых файла без пропусков. Исходные файлы находятся в `examples/tools/compose-site/`. [Dockerfile](../../../../examples/tools/compose-site/Dockerfile) · [compose.yaml](../../../../examples/tools/compose-site/compose.yaml).

| Сервис | За что отвечает | Именованный том | Сеть |
| --- | --- | --- | --- |
| `gateway` | Принимает HTTP-запросы и выбирает раздел | `requests` — журнал запросов | `catalog-net` и `help-net` |
| `catalog` | Отдаёт текст каталога | `catalog-pages` — файлы каталога | `catalog-net` |
| `help` | Отдаёт текст справки | `help-pages` — файлы справки | `help-net` |

## Dockerfile

Один [Dockerfile](../../../../examples/tools/compose-site/Dockerfile) задаёт образ для каталога и справки. У каждого сервиса Compose выбирает свой рабочий каталог.

```dockerfile
FROM python:3.14-slim
WORKDIR /site
COPY --chown=10001:10001 pages/ ./
USER 10001:10001
EXPOSE 8000
STOPSIGNAL SIGINT
CMD ["python", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
```

## compose.yaml

В полном [compose.yaml](../../../../examples/tools/compose-site/compose.yaml) шлюз использует готовый образ Nginx. Порт на компьютере нужен только шлюзу.

```yaml
services:
  gateway:
    image: nginx:stable-alpine
    ports:
      - "127.0.0.1:${SITE_PORT:-18083}:80"
    volumes:
      - ./gateway.conf:/etc/nginx/conf.d/default.conf:ro
      - requests:/var/log/site
    networks: [catalog-net, help-net]
    depends_on: [catalog, help]

  catalog:
    build: .
    working_dir: /site/catalog
    volumes:
      - catalog-pages:/site/catalog
    networks: [catalog-net]

  help:
    build: .
    working_dir: /site/help
    volumes:
      - help-pages:/site/help
    networks: [help-net]

volumes:
  requests:
  catalog-pages:
  help-pages:

networks:
  catalog-net:
  help-net:
```

Для запуска рядом с этими файлами нужны [маршруты Nginx](../../../../examples/tools/compose-site/gateway.conf), [текст каталога](../../../../examples/tools/compose-site/pages/catalog/message.txt) и [текст справки](../../../../examples/tools/compose-site/pages/help/message.txt). Файл [.dockerignore](../../../../examples/tools/compose-site/.dockerignore) оставляет в контексте сборки каталог страниц.

<details>
<summary>Полный gateway.conf — где задаются маршруты</summary>

[Исходный gateway.conf](../../../../examples/tools/compose-site/gateway.conf)

```nginx
server {
    listen 80;
    access_log /var/log/site/requests.log;

    location /catalog/ {
        proxy_pass http://catalog:8000/;
    }

    location /help/ {
        proxy_pass http://help:8000/;
    }
}
```

Запись `proxy_pass http://catalog:8000/;` со слешем в конце заменяет префикс `/catalog/` на `/`. Так запрос `/catalog/message.txt` попадает на сервер каталога как `/message.txt`. [proxy_pass](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass).

</details>

## Запуск

Запустите Docker Desktop или Docker Engine с плагином Compose. Нужны Linux-контейнеры, curl 7.71 или новее, свободный порт `18083` и доступ к Docker Hub при первой загрузке образов. Команды рассчитаны на Bash или Zsh. Сервер Python предназначен для локального учебного запуска. Для первого прогона используйте проект с пустыми учебными томами.

Из корня репозитория выполните следующий блок. Остальные команды выполняйте из того же каталога.

```bash
cd examples/tools/compose-site
docker compose config -q
docker compose up -d --build
docker compose ps
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/catalog/message.txt
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/help/message.txt
```

В списке появятся три работающих сервиса. Два запроса вернут разные строки.

```text
Catalog is ready.
Help is ready.
```

Если порт занят, задайте свободный порт командой `export SITE_PORT=18084` перед запуском. Используйте тот же порт в запросах. Если шлюз возвращает HTTP 502, проверьте `docker compose logs --tail 20 gateway catalog help`. При старте возможен краткий ответ 502, пока внутренний сервер начинает принимать запросы. Команда curl повторит запрос. Если контейнер раздела пересоздали отдельно и его адрес изменился, выполните `docker compose restart gateway`, чтобы Nginx снова разрешил имя сервиса.

## Задание 1. Проследить запрос

Найдите оба запроса в томе шлюза.

```bash
docker compose exec gateway tail -n 5 /var/log/site/requests.log
```

Для каждого маршрута найдите строку с кодом `200`. Прочитайте столбец `PORTS` в выводе `docker compose ps`. Только у `gateway` указан адрес компьютера. Внутри сетей шлюз использует имена сервисов. [Схема движения запроса](guide.md).

Посмотрите тот же запрос со стороны шлюза. Внутри его контейнера обе страницы доступны по имени сервиса и внутреннему порту.

```bash
docker compose exec gateway wget -qO- http://catalog:8000/message.txt
docker compose exec gateway wget -qO- http://help:8000/message.txt
```

## Задание 2. Проверить том после пересоздания

Измените только учебный текст каталога. Команда перезапишет `message.txt` внутри тома `catalog-pages`. Исходный файл в репозитории сохранится.

```bash
docker compose exec catalog sh -c 'echo "Catalog updated." > message.txt'
docker compose down
docker compose up -d
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/catalog/message.txt
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18083/help/message.txt
```

Каталог вернёт `Catalog updated.`, справка — прежний текст. Имя проекта и каталог запуска должны остаться прежними, чтобы Compose подключил те же тома.

## Завершение

Выполните `docker compose down`, чтобы удалить контейнеры и сети. Тома сохранятся для следующего запуска. Если нужен полный сброс этого учебного проекта, выполните `docker compose down -v`. Команда удалит все три именованных тома, включая изменённую страницу и журнал запросов.

[Все материалы по Docker](README.md)
