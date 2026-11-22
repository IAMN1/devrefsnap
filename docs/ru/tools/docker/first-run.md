# Первый запуск одного сервиса

[English](../../../en/tools/docker/first-run.md)

Короткое упражнение для первого знакомства с Docker. Сервер отдаёт один текстовый файл. Для примера с тремя сервисами откройте [практикум](lab.md).

## Первый запуск

Запустите Docker Desktop или Docker Engine с плагином Compose. Выполняйте команды в Bash или Zsh из корня репозитория. Для первого запуска нужны curl 7.71 или новее и доступ к Docker Hub. По умолчанию пример занимает локальный порт `18081`. Сервер Python предназначен для учебного запуска. [Установка Compose](https://docs.docker.com/compose/install/) · [Модуль http.server](https://docs.python.org/3.14/library/http.server.html).

```bash
cd examples/tools/docker-basics
docker version
docker compose version
docker compose config -q
docker compose up --build -d
docker compose ps
curl --retry 5 --retry-all-errors -fsS http://127.0.0.1:18081/message.txt
```

У `docker version` должна появиться секция `Server`. Команда `config -q` при успехе завершится без вывода. Команда `up` соберёт образ по [Dockerfile](../../../../examples/tools/docker-basics/Dockerfile) и запустит сервис `web` из [compose.yaml](../../../../examples/tools/docker-basics/compose.yaml). Флаг `-d` вернёт управление терминалу.

В выводе `ps` найдите сервис `web` и привязку `127.0.0.1:18081->8000/tcp`. Если сервер ещё запускается, curl может показать ошибку соединения и повторить запрос. При успехе вы увидите содержимое [message.txt](../../../../examples/tools/docker-basics/message.txt).

```text
Hello from Docker!
```

Посмотрите запись о запросе. Затем удалите учебный контейнер и сеть проекта. Собранный образ останется на компьютере.

```bash
docker compose logs --tail 5 web
docker compose down
```

## Применить изменение

В отдельной учебной копии каталога примера выполните `docker compose up -d --build`. Замените строку в `message.txt` на `Hello again!`. В базовой конфигурации Dockerfile копирует этот файл в образ, а Compose запускает контейнер без привязки файла с компьютера.

```bash
docker compose restart web
docker compose exec web cat message.txt
docker compose up -d --build web
docker compose exec web cat message.txt
```

После `restart` вы увидите `Hello from Docker!`. После сборки и пересоздания контейнера появится `Hello again!`. Завершите упражнение командой `docker compose down`.

[Все материалы по Docker](README.md)
