# Dockerfile и Docker Compose

[English](../../../en/tools/docker/README.md)

| Что вам нужно | Куда перейти |
| --- | --- |
| Быстро вспомнить синтаксис | **Шпаргалки** — [инструкции Dockerfile](dockerfile.md), [поля compose.yaml](compose-file.md), [команды Compose](commands.md) |
| Понять, как файлы работают вместе | **Методичка** — [от сборки образа до запроса через два контейнера](guide.md) |
| Посмотреть готовые файлы целиком или выполнить задания | **Практикум** — [полный Dockerfile](lab.md#dockerfile), [полный compose.yaml для трёх сервисов](lab.md#composeyaml), [запуск и задания](lab.md#запуск) |

[Dockerfile в `dockers/`, `main.py` и `.dockerignore` в корне: дерево файлов и обе конфигурации Compose](build-context.md).

## Первый запуск

[Упражнение с одним сервисом](first-run.md) подходит, если вы впервые запускаете Docker. В [итоговом примере](lab.md) шлюз направляет запросы в каталог и справку. У каждого сервиса есть именованный том и явно указанная сеть.

[Приложение с PostgreSQL и тест в GitHub Actions](../compose-and-github-actions.md) · [Инструменты разработки](../README.md)
