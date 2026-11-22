# Проверка файлов и маршрутов читателя

22 ноября 2026 года проверили исходные 518 файлов коммита `3bd6c05` и рабочее дерево после правок. Итоговый список содержит 630 файлов, включая этот отчёт. Имена взяты из `git ls-files -co --exclude-standard`. В таблицах ниже есть запись для каждого другого файла. Парные страницы объединены в одну строку.

## Что нашёл бы читатель

| Вопрос | Исправление и проверка |
| --- | --- |
| Как собрать проект, если Dockerfile лежит ниже исходников? | Из [корневого README](../../README.md) есть прямой переход на [дерево, файлы и команды](../../docs/ru/tools/docker/build-context.md). Docker CLI и оба варианта Compose вывели `/app/main.py`. |
| Почему открывается 404 после переноса раздела? | Восстановили 103 старые страницы перехода. Проверили их ссылки и исторические якоря. Старое руководство GNU Findutils имело отдельную причину отказа. [Внутренние адреса](internal-links.md) · [Внешние адреса](external-links.md) |
| Как получить работающую базу после команды из шпаргалки? | На SQLite проверка кода завершения пропускала пустую БД. Исправленная команда создала таблицы, а контрольный запрос вернул ожидаемые строки. [Подробности прогона](database-checks.md) |
| Где команда, объяснение и полный код? | В теме Docker есть три отдельных входа. В каталоге примеров файлы сгруппированы по теме. Для архитектурных примеров указана команда из корня клона. [Сравнение исходных материалов и выбор форматов](reference-formats.md) · [Каталог примеров](../../examples/README.md) |

## Что проверено

Проверка навигации построила граф переходов отдельно для каждого языка. Начальная страница — каталог этого языка. В маршруте разрешены только Markdown-ссылки внутри той же версии. Все 136 страниц в каждом каталоге доступны максимум за три перехода. Каждая содержит ссылку на парную страницу. Количество переходов измеряет структуру ссылок. Для наблюдения за реальным поиском есть [задания читателям](../plans/reader-check.md).

Все 26 изображений используются в материалах. Для 11 GIF декодировали каждый кадр. Для 15 SVG разобрали XML и проверили область просмотра. Все 96 блоков Mermaid отрисовали в непустой SVG в Chromium. Проверили подписи Markdown-изображений. Это техническая проверка отображения. Читаемость со скринридером требует отдельного прогона.

Все файлы Python скомпилировали, shell-файлы проверили через `bash -n`. Разобрали JSON, YAML, XML проектов, TOML и INI. Для каждого файла Compose выполнили `docker compose -f <файл> config -q`. Бинарные изображения и тексты лицензий проверяли в исходном формате.

| Что выполняли | Что подтвердилось |
| --- | --- |
| Docker Engine 29.9.3, Compose 5.7.0, учебные проекты | Команда с `-f dockers/Dockerfile` и оба файла Compose дали один путь программы. Тестовая сборка с `COPY . /` перенесла исходник и исключила три синтетических объекта. Пересоздание контейнеров сохранило изменённую страницу каталога в именованном томе. Оба маршрута шлюза вернули ожидаемый текст. PostgreSQL прошёл тест подключения. Клиент контракта получил 200 для книги и 404 для отсутствующей записи. |
| Архитектура и алгоритмы | Выполнили восемь Python-файлов архитектуры и подсчёт операций. Для размеров 4, 8 и 16 вложенный цикл дал 16, 64 и 256. Проверки контрактов и повторной публикации Outbox прошли на учебных данных. |
| Linux, Git и HTTP | Три программы Linux проверили файлы, сигналы и PID слушающего процесса в одноразовом Linux-контейнере. Четыре Git-сценария прошли во временных репозиториях. Запрос к локальному JSON дал HTTP 200 и поле `Book`. |
| Языки и БД | [Проверки Python и зависимостей](python-checks.md) · [C, C++, C#, Go и TypeScript](general-checks.md) · [SQL, PostgreSQL, SQLite и Redis](database-checks.md) |

Закреплённые учебные наборы имеют собственные версии зависимостей. Даты и версии исторических прогонов приведены в соответствующих отчётах. В этот проход не входили все комбинации версий, Windows, производственная нагрузка и наблюдение за независимыми читателями. Таблицы ниже различают разбор файла и фактический запуск проекта.

## Охват по файлам

У Markdown указаны число различных имён якорей и число целей ссылок с повторами. В таблице языковых версий «пер.» означает кратчайший путь от каталога. Каждый заголовок ниже разворачивает список файлов.

<details>
<summary>Читательские страницы · 272</summary>

| Путь в языковом каталоге | Русская страница | Английская страница |
| --- | --- | --- |
| README.md | [RU](../../docs/ru/README.md) 6 як., 90 ссыл., 0 пер. | [EN](../../docs/en/README.md) 11 як., 90 ссыл., 0 пер. |
| algorithms/README.md | [RU](../../docs/ru/algorithms/README.md) 6 як., 12 ссыл., 1 пер. | [EN](../../docs/en/algorithms/README.md) 6 як., 12 ссыл., 1 пер. |
| architecture/README.md | [RU](../../docs/ru/architecture/README.md) 3 як., 19 ссыл., 1 пер. | [EN](../../docs/en/architecture/README.md) 6 як., 19 ссыл., 1 пер. |
| architecture/contracts.md | [RU](../../docs/ru/architecture/contracts.md) 5 як., 13 ссыл., 1 пер. | [EN](../../docs/en/architecture/contracts.md) 10 як., 13 ссыл., 1 пер. |
| architecture/patterns/README.md | [RU](../../docs/ru/architecture/patterns/README.md) 10 як., 27 ссыл., 1 пер. | [EN](../../docs/en/architecture/patterns/README.md) 17 як., 27 ссыл., 1 пер. |
| architecture/patterns/architecture-patterns.md | [RU](../../docs/ru/architecture/patterns/architecture-patterns.md) 13 як., 34 ссыл., 2 пер. | [EN](../../docs/en/architecture/patterns/architecture-patterns.md) 24 як., 34 ссыл., 2 пер. |
| architecture/patterns/code-examples.md | [RU](../../docs/ru/architecture/patterns/code-examples.md) 7 як., 17 ссыл., 1 пер. | [EN](../../docs/en/architecture/patterns/code-examples.md) 14 як., 17 ссыл., 1 пер. |
| architecture/patterns/design-patterns.md | [RU](../../docs/ru/architecture/patterns/design-patterns.md) 20 як., 33 ссыл., 2 пер. | [EN](../../docs/en/architecture/patterns/design-patterns.md) 37 як., 33 ссыл., 2 пер. |
| architecture/patterns/distributed-systems.md | [RU](../../docs/ru/architecture/patterns/distributed-systems.md) 9 як., 25 ссыл., 1 пер. | [EN](../../docs/en/architecture/patterns/distributed-systems.md) 18 як., 25 ссыл., 1 пер. |
| architecture/patterns/outbox-example.md | [RU](../../docs/ru/architecture/patterns/outbox-example.md) 4 як., 9 ссыл., 1 пер. | [EN](../../docs/en/architecture/patterns/outbox-example.md) 7 як., 9 ссыл., 1 пер. |
| architecture/principles.md | [RU](../../docs/ru/architecture/principles.md) 13 як., 24 ссыл., 1 пер. | [EN](../../docs/en/architecture/principles.md) 23 як., 24 ссыл., 1 пер. |
| architecture/solid.md | [RU](../../docs/ru/architecture/solid.md) 14 як., 23 ссыл., 1 пер. | [EN](../../docs/en/architecture/solid.md) 24 як., 23 ссыл., 1 пер. |
| c/README.md | [RU](../../docs/ru/c/README.md) 7 як., 17 ссыл., 1 пер. | [EN](../../docs/en/c/README.md) 7 як., 17 ссыл., 1 пер. |
| c/practice.md | [RU](../../docs/ru/c/practice.md) 10 як., 18 ссыл., 1 пер. | [EN](../../docs/en/c/practice.md) 10 як., 18 ссыл., 1 пер. |
| c/syntax.md | [RU](../../docs/ru/c/syntax.md) 6 як., 13 ссыл., 1 пер. | [EN](../../docs/en/c/syntax.md) 6 як., 13 ссыл., 1 пер. |
| c/tooling-and-testing.md | [RU](../../docs/ru/c/tooling-and-testing.md) 8 як., 29 ссыл., 1 пер. | [EN](../../docs/en/c/tooling-and-testing.md) 8 як., 29 ссыл., 1 пер. |
| cpp/README.md | [RU](../../docs/ru/cpp/README.md) 7 як., 20 ссыл., 1 пер. | [EN](../../docs/en/cpp/README.md) 7 як., 20 ссыл., 1 пер. |
| cpp/practice.md | [RU](../../docs/ru/cpp/practice.md) 9 як., 26 ссыл., 1 пер. | [EN](../../docs/en/cpp/practice.md) 9 як., 26 ссыл., 1 пер. |
| cpp/syntax.md | [RU](../../docs/ru/cpp/syntax.md) 16 як., 18 ссыл., 1 пер. | [EN](../../docs/en/cpp/syntax.md) 16 як., 18 ссыл., 1 пер. |
| cpp/tooling-and-testing.md | [RU](../../docs/ru/cpp/tooling-and-testing.md) 13 як., 38 ссыл., 1 пер. | [EN](../../docs/en/cpp/tooling-and-testing.md) 12 як., 38 ссыл., 1 пер. |
| csharp/README.md | [RU](../../docs/ru/csharp/README.md) 7 як., 23 ссыл., 1 пер. | [EN](../../docs/en/csharp/README.md) 7 як., 23 ссыл., 1 пер. |
| csharp/first-http-service.md | [RU](../../docs/ru/csharp/first-http-service.md) 8 як., 16 ссыл., 1 пер. | [EN](../../docs/en/csharp/first-http-service.md) 8 як., 16 ссыл., 1 пер. |
| csharp/persist-orders.md | [RU](../../docs/ru/csharp/persist-orders.md) 9 як., 13 ссыл., 1 пер. | [EN](../../docs/en/csharp/persist-orders.md) 9 як., 13 ссыл., 1 пер. |
| csharp/practice.md | [RU](../../docs/ru/csharp/practice.md) 10 як., 41 ссыл., 1 пер. | [EN](../../docs/en/csharp/practice.md) 8 як., 41 ссыл., 1 пер. |
| csharp/syntax.md | [RU](../../docs/ru/csharp/syntax.md) 19 як., 25 ссыл., 1 пер. | [EN](../../docs/en/csharp/syntax.md) 12 як., 25 ссыл., 1 пер. |
| csharp/tooling-and-testing.md | [RU](../../docs/ru/csharp/tooling-and-testing.md) 10 як., 32 ссыл., 1 пер. | [EN](../../docs/en/csharp/tooling-and-testing.md) 10 як., 32 ссыл., 1 пер. |
| databases/README.md | [RU](../../docs/ru/databases/README.md) 3 як., 15 ссыл., 1 пер. | [EN](../../docs/en/databases/README.md) 6 як., 15 ссыл., 1 пер. |
| databases/non-relational/redis/README.md | [RU](../../docs/ru/databases/non-relational/redis/README.md) 11 як., 24 ссыл., 1 пер. | [EN](../../docs/en/databases/non-relational/redis/README.md) 17 як., 24 ссыл., 1 пер. |
| databases/non-relational/redis/aof-backup-and-restore.md | [RU](../../docs/ru/databases/non-relational/redis/aof-backup-and-restore.md) 7 як., 24 ссыл., 1 пер. | [EN](../../docs/en/databases/non-relational/redis/aof-backup-and-restore.md) 14 як., 24 ссыл., 1 пер. |
| databases/non-relational/redis/backup-and-restore.md | [RU](../../docs/ru/databases/non-relational/redis/backup-and-restore.md) 7 як., 22 ссыл., 1 пер. | [EN](../../docs/en/databases/non-relational/redis/backup-and-restore.md) 14 як., 22 ссыл., 1 пер. |
| databases/non-relational/redis/data-and-caching.md | [RU](../../docs/ru/databases/non-relational/redis/data-and-caching.md) 8 як., 18 ссыл., 2 пер. | [EN](../../docs/en/databases/non-relational/redis/data-and-caching.md) 15 як., 18 ссыл., 2 пер. |
| databases/non-relational/redis/data-lab.md | [RU](../../docs/ru/databases/non-relational/redis/data-lab.md) 4 як., 14 ссыл., 2 пер. | [EN](../../docs/en/databases/non-relational/redis/data-lab.md) 8 як., 14 ссыл., 2 пер. |
| databases/non-relational/redis/operations.md | [RU](../../docs/ru/databases/non-relational/redis/operations.md) 9 як., 26 ссыл., 2 пер. | [EN](../../docs/en/databases/non-relational/redis/operations.md) 18 як., 26 ссыл., 2 пер. |
| databases/non-relational/redis/transactions-and-messaging.md | [RU](../../docs/ru/databases/non-relational/redis/transactions-and-messaging.md) 8 як., 23 ссыл., 2 пер. | [EN](../../docs/en/databases/non-relational/redis/transactions-and-messaging.md) 14 як., 23 ссыл., 2 пер. |
| databases/non-relational/redis/transactions-lab.md | [RU](../../docs/ru/databases/non-relational/redis/transactions-lab.md) 6 як., 20 ссыл., 2 пер. | [EN](../../docs/en/databases/non-relational/redis/transactions-lab.md) 10 як., 20 ссыл., 2 пер. |
| databases/relational/postgresql/README.md | [RU](../../docs/ru/databases/relational/postgresql/README.md) 11 як., 35 ссыл., 1 пер. | [EN](../../docs/en/databases/relational/postgresql/README.md) 17 як., 35 ссыл., 1 пер. |
| databases/relational/postgresql/backup-and-restore.md | [RU](../../docs/ru/databases/relational/postgresql/backup-and-restore.md) 12 як., 32 ссыл., 1 пер. | [EN](../../docs/en/databases/relational/postgresql/backup-and-restore.md) 24 як., 32 ссыл., 1 пер. |
| databases/relational/postgresql/backup-lab.md | [RU](../../docs/ru/databases/relational/postgresql/backup-lab.md) 6 як., 18 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/postgresql/backup-lab.md) 12 як., 18 ссыл., 2 пер. |
| databases/relational/postgresql/operations.md | [RU](../../docs/ru/databases/relational/postgresql/operations.md) 10 як., 34 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/postgresql/operations.md) 19 як., 34 ссыл., 2 пер. |
| databases/relational/postgresql/queries.md | [RU](../../docs/ru/databases/relational/postgresql/queries.md) 11 як., 19 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/postgresql/queries.md) 20 як., 19 ссыл., 2 пер. |
| databases/relational/postgresql/query-lab.md | [RU](../../docs/ru/databases/relational/postgresql/query-lab.md) 3 як., 16 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/postgresql/query-lab.md) 6 як., 16 ссыл., 2 пер. |
| databases/relational/postgresql/schema-and-indexes.md | [RU](../../docs/ru/databases/relational/postgresql/schema-and-indexes.md) 10 як., 21 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/postgresql/schema-and-indexes.md) 19 як., 21 ссыл., 2 пер. |
| databases/relational/sqlite/README.md | [RU](../../docs/ru/databases/relational/sqlite/README.md) 11 як., 27 ссыл., 1 пер. | [EN](../../docs/en/databases/relational/sqlite/README.md) 17 як., 27 ссыл., 1 пер. |
| databases/relational/sqlite/backup-and-migrations.md | [RU](../../docs/ru/databases/relational/sqlite/backup-and-migrations.md) 5 як., 17 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/sqlite/backup-and-migrations.md) 9 як., 17 ссыл., 2 пер. |
| databases/relational/sqlite/backup-and-restore.md | [RU](../../docs/ru/databases/relational/sqlite/backup-and-restore.md) 10 як., 29 ссыл., 1 пер. | [EN](../../docs/en/databases/relational/sqlite/backup-and-restore.md) 20 як., 29 ссыл., 1 пер. |
| databases/relational/sqlite/backup-lab.md | [RU](../../docs/ru/databases/relational/sqlite/backup-lab.md) 4 як., 15 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/sqlite/backup-lab.md) 8 як., 15 ссыл., 2 пер. |
| databases/relational/sqlite/migration-lab.md | [RU](../../docs/ru/databases/relational/sqlite/migration-lab.md) 3 як., 13 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/sqlite/migration-lab.md) 6 як., 13 ссыл., 2 пер. |
| databases/relational/sqlite/python-and-queries.md | [RU](../../docs/ru/databases/relational/sqlite/python-and-queries.md) 8 як., 21 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/sqlite/python-and-queries.md) 15 як., 21 ссыл., 2 пер. |
| databases/relational/sqlite/query-lab.md | [RU](../../docs/ru/databases/relational/sqlite/query-lab.md) 3 як., 15 ссыл., 2 пер. | [EN](../../docs/en/databases/relational/sqlite/query-lab.md) 6 як., 14 ссыл., 2 пер. |
| databases/sql/README.md | [RU](../../docs/ru/databases/sql/README.md) 11 як., 24 ссыл., 1 пер. | [EN](../../docs/en/databases/sql/README.md) 17 як., 24 ссыл., 1 пер. |
| databases/sql/dialects-and-transactions.md | [RU](../../docs/ru/databases/sql/dialects-and-transactions.md) 7 як., 18 ссыл., 2 пер. | [EN](../../docs/en/databases/sql/dialects-and-transactions.md) 14 як., 18 ссыл., 2 пер. |
| databases/sql/queries.md | [RU](../../docs/ru/databases/sql/queries.md) 11 як., 25 ссыл., 1 пер. | [EN](../../docs/en/databases/sql/queries.md) 18 як., 25 ссыл., 1 пер. |
| databases/sql/query-lab.md | [RU](../../docs/ru/databases/sql/query-lab.md) 3 як., 20 ссыл., 2 пер. | [EN](../../docs/en/databases/sql/query-lab.md) 6 як., 20 ссыл., 2 пер. |
| go/README.md | [RU](../../docs/ru/go/README.md) 12 як., 35 ссыл., 1 пер. | [EN](../../docs/en/go/README.md) 20 як., 35 ссыл., 1 пер. |
| go/concurrency-and-testing.md | [RU](../../docs/ru/go/concurrency-and-testing.md) 6 як., 21 ссыл., 2 пер. | [EN](../../docs/en/go/concurrency-and-testing.md) 12 як., 21 ссыл., 2 пер. |
| go/context.md | [RU](../../docs/ru/go/context.md) 5 як., 17 ссыл., 1 пер. | [EN](../../docs/en/go/context.md) 5 як., 17 ссыл., 1 пер. |
| go/examples/concurrency-and-testing.md | [RU](../../docs/ru/go/examples/concurrency-and-testing.md) 5 як., 18 ссыл., 3 пер. | [EN](../../docs/en/go/examples/concurrency-and-testing.md) 10 як., 18 ссыл., 3 пер. |
| go/examples/http-json.md | [RU](../../docs/ru/go/examples/http-json.md) 5 як., 14 ссыл., 3 пер. | [EN](../../docs/en/go/examples/http-json.md) 10 як., 14 ссыл., 3 пер. |
| go/examples/language.md | [RU](../../docs/ru/go/examples/language.md) 5 як., 17 ссыл., 1 пер. | [EN](../../docs/en/go/examples/language.md) 9 як., 17 ссыл., 1 пер. |
| go/http-json.md | [RU](../../docs/ru/go/http-json.md) 6 як., 17 ссыл., 2 пер. | [EN](../../docs/en/go/http-json.md) 12 як., 17 ссыл., 2 пер. |
| go/language.md | [RU](../../docs/ru/go/language.md) 8 як., 23 ссыл., 2 пер. | [EN](../../docs/en/go/language.md) 16 як., 23 ссыл., 2 пер. |
| python/README.md | [RU](../../docs/ru/python/README.md) 4 як., 27 ссыл., 1 пер. | [EN](../../docs/en/python/README.md) 6 як., 27 ссыл., 1 пер. |
| python/architecture/project-design/README.md | [RU](../../docs/ru/python/architecture/project-design/README.md) 13 як., 24 ссыл., 1 пер. | [EN](../../docs/en/python/architecture/project-design/README.md) 21 як., 24 ссыл., 1 пер. |
| python/architecture/project-design/delivery-and-evolution.md | [RU](../../docs/ru/python/architecture/project-design/delivery-and-evolution.md) 11 як., 19 ссыл., 2 пер. | [EN](../../docs/en/python/architecture/project-design/delivery-and-evolution.md) 22 як., 19 ссыл., 2 пер. |
| python/architecture/project-design/example.md | [RU](../../docs/ru/python/architecture/project-design/example.md) 9 як., 29 ссыл., 2 пер. | [EN](../../docs/en/python/architecture/project-design/example.md) 18 як., 29 ссыл., 2 пер. |
| python/architecture/project-design/structure-and-decisions.md | [RU](../../docs/ru/python/architecture/project-design/structure-and-decisions.md) 7 як., 26 ссыл., 2 пер. | [EN](../../docs/en/python/architecture/project-design/structure-and-decisions.md) 14 як., 26 ссыл., 2 пер. |
| python/databases/sqlalchemy/README.md | [RU](../../docs/ru/python/databases/sqlalchemy/README.md) 11 як., 42 ссыл., 1 пер. | [EN](../../docs/en/python/databases/sqlalchemy/README.md) 17 як., 42 ссыл., 1 пер. |
| python/databases/sqlalchemy/async-and-operations.md | [RU](../../docs/ru/python/databases/sqlalchemy/async-and-operations.md) 4 як., 26 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/async-and-operations.md) 8 як., 26 ссыл., 2 пер. |
| python/databases/sqlalchemy/filtered-relationships.md | [RU](../../docs/ru/python/databases/sqlalchemy/filtered-relationships.md) 5 як., 15 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/filtered-relationships.md) 8 як., 15 ссыл., 2 пер. |
| python/databases/sqlalchemy/loading-lab.md | [RU](../../docs/ru/python/databases/sqlalchemy/loading-lab.md) 5 як., 19 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/loading-lab.md) 10 як., 19 ссыл., 2 пер. |
| python/databases/sqlalchemy/models-and-transactions.md | [RU](../../docs/ru/python/databases/sqlalchemy/models-and-transactions.md) 3 як., 20 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/models-and-transactions.md) 6 як., 20 ссыл., 2 пер. |
| python/databases/sqlalchemy/n-plus-one.md | [RU](../../docs/ru/python/databases/sqlalchemy/n-plus-one.md) 7 як., 23 ссыл., 1 пер. | [EN](../../docs/en/python/databases/sqlalchemy/n-plus-one.md) 7 як., 23 ссыл., 1 пер. |
| python/databases/sqlalchemy/queries.md | [RU](../../docs/ru/python/databases/sqlalchemy/queries.md) 5 як., 20 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/queries.md) 10 як., 20 ссыл., 2 пер. |
| python/databases/sqlalchemy/relationship-loading.md | [RU](../../docs/ru/python/databases/sqlalchemy/relationship-loading.md) 15 як., 46 ссыл., 1 пер. | [EN](../../docs/en/python/databases/sqlalchemy/relationship-loading.md) 28 як., 46 ссыл., 1 пер. |
| python/databases/sqlalchemy/streaming.md | [RU](../../docs/ru/python/databases/sqlalchemy/streaming.md) 5 як., 16 ссыл., 2 пер. | [EN](../../docs/en/python/databases/sqlalchemy/streaming.md) 10 як., 16 ссыл., 2 пер. |
| python/language/asyncio.md | [RU](../../docs/ru/python/language/asyncio.md) 7 як., 13 ссыл., 1 пер. | [EN](../../docs/en/python/language/asyncio.md) 7 як., 13 ссыл., 1 пер. |
| python/language/first-program.md | [RU](../../docs/ru/python/language/first-program.md) 3 як., 5 ссыл., 1 пер. | [EN](../../docs/en/python/language/first-program.md) 3 як., 5 ссыл., 1 пер. |
| python/language/read-lines.md | [RU](../../docs/ru/python/language/read-lines.md) 1 як., 4 ссыл., 1 пер. | [EN](../../docs/en/python/language/read-lines.md) 1 як., 4 ссыл., 1 пер. |
| python/language/types/README.md | [RU](../../docs/ru/python/language/types/README.md) 12 як., 28 ссыл., 1 пер. | [EN](../../docs/en/python/language/types/README.md) 21 як., 28 ссыл., 1 пер. |
| python/language/types/recipes.md | [RU](../../docs/ru/python/language/types/recipes.md) 3 як., 7 ссыл., 2 пер. | [EN](../../docs/en/python/language/types/recipes.md) 6 як., 7 ссыл., 2 пер. |
| python/logging/structlog/README.md | [RU](../../docs/ru/python/logging/structlog/README.md) 11 як., 25 ссыл., 1 пер. | [EN](../../docs/en/python/logging/structlog/README.md) 17 як., 25 ссыл., 1 пер. |
| python/logging/structlog/configuration.md | [RU](../../docs/ru/python/logging/structlog/configuration.md) 4 як., 19 ссыл., 2 пер. | [EN](../../docs/en/python/logging/structlog/configuration.md) 8 як., 19 ссыл., 2 пер. |
| python/logging/structlog/context-and-web.md | [RU](../../docs/ru/python/logging/structlog/context-and-web.md) 4 як., 19 ссыл., 2 пер. | [EN](../../docs/en/python/logging/structlog/context-and-web.md) 8 як., 19 ссыл., 2 пер. |
| python/testing/pytest/README.md | [RU](../../docs/ru/python/testing/pytest/README.md) 11 як., 31 ссыл., 1 пер. | [EN](../../docs/en/python/testing/pytest/README.md) 17 як., 31 ссыл., 1 пер. |
| python/testing/pytest/configuration.md | [RU](../../docs/ru/python/testing/pytest/configuration.md) 6 як., 12 ссыл., 2 пер. | [EN](../../docs/en/python/testing/pytest/configuration.md) 12 як., 12 ссыл., 2 пер. |
| python/testing/pytest/fixtures.md | [RU](../../docs/ru/python/testing/pytest/fixtures.md) 5 як., 11 ссыл., 2 пер. | [EN](../../docs/en/python/testing/pytest/fixtures.md) 10 як., 11 ссыл., 2 пер. |
| python/testing/pytest/mocking-and-async.md | [RU](../../docs/ru/python/testing/pytest/mocking-and-async.md) 5 як., 15 ссыл., 2 пер. | [EN](../../docs/en/python/testing/pytest/mocking-and-async.md) 10 як., 15 ссыл., 2 пер. |
| python/tooling/uv/README.md | [RU](../../docs/ru/python/tooling/uv/README.md) 11 як., 28 ссыл., 1 пер. | [EN](../../docs/en/python/tooling/uv/README.md) 17 як., 28 ссыл., 1 пер. |
| python/tooling/uv/automation.md | [RU](../../docs/ru/python/tooling/uv/automation.md) 7 як., 14 ссыл., 2 пер. | [EN](../../docs/en/python/tooling/uv/automation.md) 12 як., 14 ссыл., 2 пер. |
| python/tooling/uv/projects.md | [RU](../../docs/ru/python/tooling/uv/projects.md) 7 як., 12 ссыл., 2 пер. | [EN](../../docs/en/python/tooling/uv/projects.md) 14 як., 12 ссыл., 2 пер. |
| python/validation/pydantic/README.md | [RU](../../docs/ru/python/validation/pydantic/README.md) 11 як., 25 ссыл., 1 пер. | [EN](../../docs/en/python/validation/pydantic/README.md) 17 як., 25 ссыл., 1 пер. |
| python/validation/pydantic/advanced.md | [RU](../../docs/ru/python/validation/pydantic/advanced.md) 5 як., 22 ссыл., 2 пер. | [EN](../../docs/en/python/validation/pydantic/advanced.md) 10 як., 22 ссыл., 2 пер. |
| python/validation/pydantic/models.md | [RU](../../docs/ru/python/validation/pydantic/models.md) 3 як., 17 ссыл., 2 пер. | [EN](../../docs/en/python/validation/pydantic/models.md) 6 як., 17 ссыл., 2 пер. |
| python/web/django/README.md | [RU](../../docs/ru/python/web/django/README.md) 6 як., 18 ссыл., 1 пер. | [EN](../../docs/en/python/web/django/README.md) 6 як., 18 ссыл., 1 пер. |
| python/web/fastapi/README.md | [RU](../../docs/ru/python/web/fastapi/README.md) 13 як., 44 ссыл., 1 пер. | [EN](../../docs/en/python/web/fastapi/README.md) 21 як., 44 ссыл., 1 пер. |
| python/web/fastapi/authentication.md | [RU](../../docs/ru/python/web/fastapi/authentication.md) 5 як., 14 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/authentication.md) 10 як., 14 ссыл., 2 пер. |
| python/web/fastapi/database.md | [RU](../../docs/ru/python/web/fastapi/database.md) 3 як., 18 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/database.md) 6 як., 18 ссыл., 2 пер. |
| python/web/fastapi/dependency-overrides.md | [RU](../../docs/ru/python/web/fastapi/dependency-overrides.md) 8 як., 26 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/dependency-overrides.md) 15 як., 26 ссыл., 2 пер. |
| python/web/fastapi/deployment.md | [RU](../../docs/ru/python/web/fastapi/deployment.md) 6 як., 16 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/deployment.md) 12 як., 16 ссыл., 2 пер. |
| python/web/fastapi/http-api.md | [RU](../../docs/ru/python/web/fastapi/http-api.md) 2 як., 15 ссыл., 1 пер. | [EN](../../docs/en/python/web/fastapi/http-api.md) 4 як., 15 ссыл., 1 пер. |
| python/web/fastapi/middleware.md | [RU](../../docs/ru/python/web/fastapi/middleware.md) 2 як., 11 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/middleware.md) 4 як., 11 ссыл., 2 пер. |
| python/web/fastapi/recipes.md | [RU](../../docs/ru/python/web/fastapi/recipes.md) 6 як., 28 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/recipes.md) 12 як., 28 ссыл., 2 пер. |
| python/web/fastapi/testing-lab.md | [RU](../../docs/ru/python/web/fastapi/testing-lab.md) 7 як., 28 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/testing-lab.md) 14 як., 28 ссыл., 2 пер. |
| python/web/fastapi/testing.md | [RU](../../docs/ru/python/web/fastapi/testing.md) 12 як., 46 ссыл., 1 пер. | [EN](../../docs/en/python/web/fastapi/testing.md) 23 як., 46 ссыл., 1 пер. |
| python/web/fastapi/uploads.md | [RU](../../docs/ru/python/web/fastapi/uploads.md) 2 як., 12 ссыл., 2 пер. | [EN](../../docs/en/python/web/fastapi/uploads.md) 4 як., 12 ссыл., 2 пер. |
| python/web/flask/README.md | [RU](../../docs/ru/python/web/flask/README.md) 11 як., 35 ссыл., 1 пер. | [EN](../../docs/en/python/web/flask/README.md) 17 як., 35 ссыл., 1 пер. |
| python/web/flask/application.md | [RU](../../docs/ru/python/web/flask/application.md) 5 як., 14 ссыл., 2 пер. | [EN](../../docs/en/python/web/flask/application.md) 10 як., 14 ссыл., 2 пер. |
| python/web/flask/configuration-and-deployment.md | [RU](../../docs/ru/python/web/flask/configuration-and-deployment.md) 5 як., 16 ссыл., 2 пер. | [EN](../../docs/en/python/web/flask/configuration-and-deployment.md) 10 як., 16 ссыл., 2 пер. |
| python/web/flask/testing.md | [RU](../../docs/ru/python/web/flask/testing.md) 4 як., 9 ссыл., 2 пер. | [EN](../../docs/en/python/web/flask/testing.md) 8 як., 9 ссыл., 2 пер. |
| systems/README.md | [RU](../../docs/ru/systems/README.md) 1 як., 6 ссыл., 1 пер. | [EN](../../docs/en/systems/README.md) 2 як., 6 ссыл., 1 пер. |
| systems/linux/README.md | [RU](../../docs/ru/systems/linux/README.md) 11 як., 36 ссыл., 1 пер. | [EN](../../docs/en/systems/linux/README.md) 19 як., 36 ссыл., 1 пер. |
| systems/linux/network-and-services.md | [RU](../../docs/ru/systems/linux/network-and-services.md) 6 як., 17 ссыл., 2 пер. | [EN](../../docs/en/systems/linux/network-and-services.md) 12 як., 17 ссыл., 2 пер. |
| systems/linux/permissions-and-processes.md | [RU](../../docs/ru/systems/linux/permissions-and-processes.md) 5 як., 14 ссыл., 2 пер. | [EN](../../docs/en/systems/linux/permissions-and-processes.md) 10 як., 14 ссыл., 2 пер. |
| systems/linux/process-by-port.md | [RU](../../docs/ru/systems/linux/process-by-port.md) 7 як., 20 ссыл., 1 пер. | [EN](../../docs/en/systems/linux/process-by-port.md) 14 як., 20 ссыл., 1 пер. |
| systems/linux/shell-and-files.md | [RU](../../docs/ru/systems/linux/shell-and-files.md) 6 як., 11 ссыл., 2 пер. | [EN](../../docs/en/systems/linux/shell-and-files.md) 12 як., 11 ссыл., 2 пер. |
| tasks/README.md | [RU](../../docs/ru/tasks/README.md) 22 як., 263 ссыл., 1 пер. | [EN](../../docs/en/tasks/README.md) 34 як., 263 ссыл., 1 пер. |
| tools/README.md | [RU](../../docs/ru/tools/README.md) 2 як., 20 ссыл., 1 пер. | [EN](../../docs/en/tools/README.md) 4 як., 20 ссыл., 1 пер. |
| tools/api-contract-lab.md | [RU](../../docs/ru/tools/api-contract-lab.md) 7 як., 26 ссыл., 1 пер. | [EN](../../docs/en/tools/api-contract-lab.md) 7 як., 26 ссыл., 1 пер. |
| tools/compose-and-github-actions.md | [RU](../../docs/ru/tools/compose-and-github-actions.md) 10 як., 30 ссыл., 1 пер. | [EN](../../docs/en/tools/compose-and-github-actions.md) 10 як., 30 ссыл., 1 пер. |
| tools/docker/README.md | [RU](../../docs/ru/tools/docker/README.md) 2 як., 13 ссыл., 1 пер. | [EN](../../docs/en/tools/docker/README.md) 2 як., 13 ссыл., 1 пер. |
| tools/docker/build-context.md | [RU](../../docs/ru/tools/docker/build-context.md) 6 як., 10 ссыл., 1 пер. | [EN](../../docs/en/tools/docker/build-context.md) 6 як., 10 ссыл., 1 пер. |
| tools/docker/commands.md | [RU](../../docs/ru/tools/docker/commands.md) 4 як., 9 ссыл., 2 пер. | [EN](../../docs/en/tools/docker/commands.md) 4 як., 9 ссыл., 2 пер. |
| tools/docker/compose-file.md | [RU](../../docs/ru/tools/docker/compose-file.md) 7 як., 21 ссыл., 2 пер. | [EN](../../docs/en/tools/docker/compose-file.md) 7 як., 21 ссыл., 2 пер. |
| tools/docker/dockerfile.md | [RU](../../docs/ru/tools/docker/dockerfile.md) 6 як., 14 ссыл., 2 пер. | [EN](../../docs/en/tools/docker/dockerfile.md) 6 як., 14 ссыл., 2 пер. |
| tools/docker/first-run.md | [RU](../../docs/ru/tools/docker/first-run.md) 3 як., 8 ссыл., 2 пер. | [EN](../../docs/en/tools/docker/first-run.md) 3 як., 8 ссыл., 2 пер. |
| tools/docker/guide.md | [RU](../../docs/ru/tools/docker/guide.md) 5 як., 7 ссыл., 1 пер. | [EN](../../docs/en/tools/docker/guide.md) 5 як., 7 ссыл., 1 пер. |
| tools/docker/lab.md | [RU](../../docs/ru/tools/docker/lab.md) 7 як., 13 ссыл., 1 пер. | [EN](../../docs/en/tools/docker/lab.md) 7 як., 13 ссыл., 1 пер. |
| tools/git/README.md | [RU](../../docs/ru/tools/git/README.md) 11 як., 45 ссыл., 1 пер. | [EN](../../docs/en/tools/git/README.md) 18 як., 45 ссыл., 1 пер. |
| tools/git/history.md | [RU](../../docs/ru/tools/git/history.md) 12 як., 33 ссыл., 2 пер. | [EN](../../docs/en/tools/git/history.md) 24 як., 33 ссыл., 2 пер. |
| tools/git/remotes.md | [RU](../../docs/ru/tools/git/remotes.md) 8 як., 25 ссыл., 2 пер. | [EN](../../docs/en/tools/git/remotes.md) 16 як., 25 ссыл., 2 пер. |
| tools/git/workflow.md | [RU](../../docs/ru/tools/git/workflow.md) 7 як., 21 ссыл., 2 пер. | [EN](../../docs/en/tools/git/workflow.md) 14 як., 21 ссыл., 2 пер. |
| tools/github-pull-requests/README.md | [RU](../../docs/ru/tools/github-pull-requests/README.md) 11 як., 26 ссыл., 1 пер. | [EN](../../docs/en/tools/github-pull-requests/README.md) 18 як., 26 ссыл., 1 пер. |
| tools/github-pull-requests/merging.md | [RU](../../docs/ru/tools/github-pull-requests/merging.md) 6 як., 15 ссыл., 2 пер. | [EN](../../docs/en/tools/github-pull-requests/merging.md) 12 як., 15 ссыл., 2 пер. |
| tools/github-pull-requests/review.md | [RU](../../docs/ru/tools/github-pull-requests/review.md) 6 як., 10 ссыл., 2 пер. | [EN](../../docs/en/tools/github-pull-requests/review.md) 12 як., 10 ссыл., 2 пер. |
| tools/http-json.md | [RU](../../docs/ru/tools/http-json.md) 5 як., 11 ссыл., 1 пер. | [EN](../../docs/en/tools/http-json.md) 5 як., 11 ссыл., 1 пер. |
| typescript/README.md | [RU](../../docs/ru/typescript/README.md) 5 як., 16 ссыл., 1 пер. | [EN](../../docs/en/typescript/README.md) 5 як., 16 ссыл., 1 пер. |

</details>

<details>
<summary>Общие примеры · 179</summary>

| Файл | Проверка |
| --- | --- |
| [examples/README.md](../../examples/README.md) | 23 як., 393 ссыл. |
| [examples/algorithms/big-o/count_operations.py](../../examples/algorithms/big-o/count_operations.py) | Компиляция Python |
| [examples/architecture/command-pattern.py](../../examples/architecture/command-pattern.py) | Компиляция Python |
| [examples/architecture/invariants.py](../../examples/architecture/invariants.py) | Компиляция Python |
| [examples/architecture/observer-pattern.py](../../examples/architecture/observer-pattern.py) | Компиляция Python |
| [examples/architecture/outbox.py](../../examples/architecture/outbox.py) | Компиляция Python |
| [examples/architecture/shipping-patterns.py](../../examples/architecture/shipping-patterns.py) | Компиляция Python |
| [examples/architecture/solid-contract.py](../../examples/architecture/solid-contract.py) | Компиляция Python |
| [examples/architecture/solid-ocp.py](../../examples/architecture/solid-ocp.py) | Компиляция Python |
| [examples/architecture/solid-srp.py](../../examples/architecture/solid-srp.py) | Компиляция Python |
| [examples/c/basics.c](../../examples/c/basics.c) | Исходник или сборочный файл учебного проекта |
| [examples/c/port-parser/CMakeLists.txt](../../examples/c/port-parser/CMakeLists.txt) | Исходник или сборочный файл учебного проекта |
| [examples/c/port-parser/main.c](../../examples/c/port-parser/main.c) | Исходник или сборочный файл учебного проекта |
| [examples/c/port-parser/port.c](../../examples/c/port-parser/port.c) | Исходник или сборочный файл учебного проекта |
| [examples/c/port-parser/port.h](../../examples/c/port-parser/port.h) | Исходник или сборочный файл учебного проекта |
| [examples/c/port-parser/test_port.c](../../examples/c/port-parser/test_port.c) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/CMakeLists.txt](../../examples/cpp/CMakeLists.txt) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/basics.cpp](../../examples/cpp/basics.cpp) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/score-count.cpp](../../examples/cpp/score-count.cpp) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/score-summary-test.cpp](../../examples/cpp/score-summary-test.cpp) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/score-summary.cpp](../../examples/cpp/score-summary.cpp) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/score-summary.hpp](../../examples/cpp/score-summary.hpp) | Исходник или сборочный файл учебного проекта |
| [examples/cpp/vcpkg.json](../../examples/cpp/vcpkg.json) | Разбор JSON |
| [examples/csharp/basics/Program.cs](../../examples/csharp/basics/Program.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/basics/basics.csproj](../../examples/csharp/basics/basics.csproj) | XML проекта .NET |
| [examples/csharp/shipping/.gitignore](../../examples/csharp/shipping/.gitignore) | Правила исключения Git |
| [examples/csharp/shipping/Orders.Api/Orders.Api.csproj](../../examples/csharp/shipping/Orders.Api/Orders.Api.csproj) | XML проекта .NET |
| [examples/csharp/shipping/Orders.Api/OrdersDb.cs](../../examples/csharp/shipping/Orders.Api/OrdersDb.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/shipping/Orders.Api/Program.cs](../../examples/csharp/shipping/Orders.Api/Program.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/shipping/Shipping.Api.Tests/Shipping.Api.Tests.csproj](../../examples/csharp/shipping/Shipping.Api.Tests/Shipping.Api.Tests.csproj) | XML проекта .NET |
| [examples/csharp/shipping/Shipping.Api.Tests/ShippingQuoteTests.cs](../../examples/csharp/shipping/Shipping.Api.Tests/ShippingQuoteTests.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/shipping/Shipping.Api/Program.cs](../../examples/csharp/shipping/Shipping.Api/Program.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/shipping/Shipping.Api/Shipping.Api.csproj](../../examples/csharp/shipping/Shipping.Api/Shipping.Api.csproj) | XML проекта .NET |
| [examples/csharp/shipping/Shipping.Tests/Shipping.Tests.csproj](../../examples/csharp/shipping/Shipping.Tests/Shipping.Tests.csproj) | XML проекта .NET |
| [examples/csharp/shipping/Shipping.Tests/ShippingFeeTests.cs](../../examples/csharp/shipping/Shipping.Tests/ShippingFeeTests.cs) | Исходник или сборочный файл учебного проекта |
| [examples/csharp/shipping/Shipping/Shipping.csproj](../../examples/csharp/shipping/Shipping/Shipping.csproj) | XML проекта .NET |
| [examples/csharp/shipping/Shipping/ShippingFee.cs](../../examples/csharp/shipping/Shipping/ShippingFee.cs) | Исходник или сборочный файл учебного проекта |
| [examples/databases/non-relational/redis/aof_backup.py](../../examples/databases/non-relational/redis/aof_backup.py) | Компиляция Python |
| [examples/databases/non-relational/redis/data.py](../../examples/databases/non-relational/redis/data.py) | Компиляция Python |
| [examples/databases/non-relational/redis/messaging.py](../../examples/databases/non-relational/redis/messaging.py) | Компиляция Python |
| [examples/databases/non-relational/redis/rdb_backup.py](../../examples/databases/non-relational/redis/rdb_backup.py) | Компиляция Python |
| [examples/databases/non-relational/redis/transactions.py](../../examples/databases/non-relational/redis/transactions.py) | Компиляция Python |
| [examples/databases/relational/postgresql/backup-lab.sh](../../examples/databases/relational/postgresql/backup-lab.sh) | bash -n |
| [examples/databases/relational/postgresql/queries.sql](../../examples/databases/relational/postgresql/queries.sql) | SQL в учебной БД |
| [examples/databases/relational/postgresql/verify-backup.sql](../../examples/databases/relational/postgresql/verify-backup.sql) | SQL в учебной БД |
| [examples/databases/relational/sqlite/backup-cli.sh](../../examples/databases/relational/sqlite/backup-cli.sh) | bash -n |
| [examples/databases/relational/sqlite/backup.py](../../examples/databases/relational/sqlite/backup.py) | Компиляция Python |
| [examples/databases/relational/sqlite/demo.py](../../examples/databases/relational/sqlite/demo.py) | Компиляция Python |
| [examples/databases/relational/sqlite/migration.py](../../examples/databases/relational/sqlite/migration.py) | Компиляция Python |
| [examples/databases/sql/demo.sql](../../examples/databases/sql/demo.sql) | SQL в учебной БД |
| [examples/go/cmd/demo/main.go](../../examples/go/cmd/demo/main.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/context/main.go](../../examples/go/context/main.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/counter.go](../../examples/go/counter.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/go.mod](../../examples/go/go.mod) | Исходник или сборочный файл учебного проекта |
| [examples/go/http.go](../../examples/go/http.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/http_test.go](../../examples/go/http_test.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/model.go](../../examples/go/model.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/model_test.go](../../examples/go/model_test.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/worker.go](../../examples/go/worker.go) | Исходник или сборочный файл учебного проекта |
| [examples/go/worker_test.go](../../examples/go/worker_test.go) | Исходник или сборочный файл учебного проекта |
| [examples/python/architecture/project-design/pyproject.toml](../../examples/python/architecture/project-design/pyproject.toml) | Разбор TOML |
| [examples/python/architecture/project-design/src/catalog_demo/__init__.py](../../examples/python/architecture/project-design/src/catalog_demo/__init__.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/__main__.py](../../examples/python/architecture/project-design/src/catalog_demo/__main__.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/adapters.py](../../examples/python/architecture/project-design/src/catalog_demo/adapters.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/application.py](../../examples/python/architecture/project-design/src/catalog_demo/application.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/bootstrap.py](../../examples/python/architecture/project-design/src/catalog_demo/bootstrap.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/config.py](../../examples/python/architecture/project-design/src/catalog_demo/config.py) | Компиляция Python |
| [examples/python/architecture/project-design/src/catalog_demo/domain.py](../../examples/python/architecture/project-design/src/catalog_demo/domain.py) | Компиляция Python |
| [examples/python/architecture/project-design/tests/test_catalog.py](../../examples/python/architecture/project-design/tests/test_catalog.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_async.py](../../examples/python/databases/sqlalchemy/demo_async.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_crud.py](../../examples/python/databases/sqlalchemy/demo_crud.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_models.py](../../examples/python/databases/sqlalchemy/demo_models.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_observe.py](../../examples/python/databases/sqlalchemy/demo_observe.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_postgresql_sql.py](../../examples/python/databases/sqlalchemy/demo_postgresql_sql.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/demo_queries.py](../../examples/python/databases/sqlalchemy/demo_queries.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/n_plus_one.py](../../examples/python/databases/sqlalchemy/n_plus_one.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_async.py](../../examples/python/databases/sqlalchemy/test_async.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_models.py](../../examples/python/databases/sqlalchemy/test_models.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_observe.py](../../examples/python/databases/sqlalchemy/test_observe.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_queries.py](../../examples/python/databases/sqlalchemy/test_queries.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_relationship_loading.py](../../examples/python/databases/sqlalchemy/test_relationship_loading.py) | Компиляция Python |
| [examples/python/databases/sqlalchemy/test_streaming.py](../../examples/python/databases/sqlalchemy/test_streaming.py) | Компиляция Python |
| [examples/python/language/asyncio/demo.py](../../examples/python/language/asyncio/demo.py) | Компиляция Python |
| [examples/python/language/read-lines.py](../../examples/python/language/read-lines.py) | Компиляция Python |
| [examples/python/language/tickets.py](../../examples/python/language/tickets.py) | Компиляция Python |
| [examples/python/language/types/demo_types.py](../../examples/python/language/types/demo_types.py) | Компиляция Python |
| [examples/python/logging/structlog/demo_context.py](../../examples/python/logging/structlog/demo_context.py) | Компиляция Python |
| [examples/python/logging/structlog/demo_logging.py](../../examples/python/logging/structlog/demo_logging.py) | Компиляция Python |
| [examples/python/logging/structlog/demo_stdlib.py](../../examples/python/logging/structlog/demo_stdlib.py) | Компиляция Python |
| [examples/python/logging/structlog/demo_web.py](../../examples/python/logging/structlog/demo_web.py) | Компиляция Python |
| [examples/python/logging/structlog/test_context.py](../../examples/python/logging/structlog/test_context.py) | Компиляция Python |
| [examples/python/logging/structlog/test_logging.py](../../examples/python/logging/structlog/test_logging.py) | Компиляция Python |
| [examples/python/logging/structlog/test_stdlib.py](../../examples/python/logging/structlog/test_stdlib.py) | Компиляция Python |
| [examples/python/logging/structlog/test_web.py](../../examples/python/logging/structlog/test_web.py) | Компиляция Python |
| [examples/python/testing/pytest/demo_service.py](../../examples/python/testing/pytest/demo_service.py) | Компиляция Python |
| [examples/python/testing/pytest/pytest.ini](../../examples/python/testing/pytest/pytest.ini) | Разбор INI |
| [examples/python/testing/pytest/test_async_mock.py](../../examples/python/testing/pytest/test_async_mock.py) | Компиляция Python |
| [examples/python/testing/pytest/test_basics.py](../../examples/python/testing/pytest/test_basics.py) | Компиляция Python |
| [examples/python/tooling/uv/project.sh](../../examples/python/tooling/uv/project.sh) | bash -n |
| [examples/python/validation/pydantic/demo_advanced.py](../../examples/python/validation/pydantic/demo_advanced.py) | Компиляция Python |
| [examples/python/validation/pydantic/demo_models.py](../../examples/python/validation/pydantic/demo_models.py) | Компиляция Python |
| [examples/python/validation/pydantic/demo_query.py](../../examples/python/validation/pydantic/demo_query.py) | Компиляция Python |
| [examples/python/validation/pydantic/demo_settings.py](../../examples/python/validation/pydantic/demo_settings.py) | Компиляция Python |
| [examples/python/validation/pydantic/demo_types.py](../../examples/python/validation/pydantic/demo_types.py) | Компиляция Python |
| [examples/python/validation/pydantic/test_advanced.py](../../examples/python/validation/pydantic/test_advanced.py) | Компиляция Python |
| [examples/python/validation/pydantic/test_models.py](../../examples/python/validation/pydantic/test_models.py) | Компиляция Python |
| [examples/python/validation/pydantic/test_query.py](../../examples/python/validation/pydantic/test_query.py) | Компиляция Python |
| [examples/python/validation/pydantic/test_settings.py](../../examples/python/validation/pydantic/test_settings.py) | Компиляция Python |
| [examples/python/validation/pydantic/test_types.py](../../examples/python/validation/pydantic/test_types.py) | Компиляция Python |
| [examples/python/web/django/.gitignore](../../examples/python/web/django/.gitignore) | Правила исключения Git |
| [examples/python/web/django/catalog/__init__.py](../../examples/python/web/django/catalog/__init__.py) | Компиляция Python |
| [examples/python/web/django/catalog/admin.py](../../examples/python/web/django/catalog/admin.py) | Компиляция Python |
| [examples/python/web/django/catalog/migrations/0001_initial.py](../../examples/python/web/django/catalog/migrations/0001_initial.py) | Компиляция Python |
| [examples/python/web/django/catalog/migrations/__init__.py](../../examples/python/web/django/catalog/migrations/__init__.py) | Компиляция Python |
| [examples/python/web/django/catalog/models.py](../../examples/python/web/django/catalog/models.py) | Компиляция Python |
| [examples/python/web/django/catalog/tests.py](../../examples/python/web/django/catalog/tests.py) | Компиляция Python |
| [examples/python/web/django/config/__init__.py](../../examples/python/web/django/config/__init__.py) | Компиляция Python |
| [examples/python/web/django/config/settings.py](../../examples/python/web/django/config/settings.py) | Компиляция Python |
| [examples/python/web/django/config/urls.py](../../examples/python/web/django/config/urls.py) | Компиляция Python |
| [examples/python/web/django/manage.py](../../examples/python/web/django/manage.py) | Компиляция Python |
| [examples/python/web/django/requirements.txt](../../examples/python/web/django/requirements.txt) | Манифест зависимостей |
| [examples/python/web/fastapi/async_db_app.py](../../examples/python/web/fastapi/async_db_app.py) | Компиляция Python |
| [examples/python/web/fastapi/auth_app.py](../../examples/python/web/fastapi/auth_app.py) | Компиляция Python |
| [examples/python/web/fastapi/db_app.py](../../examples/python/web/fastapi/db_app.py) | Компиляция Python |
| [examples/python/web/fastapi/header_dependency.py](../../examples/python/web/fastapi/header_dependency.py) | Компиляция Python |
| [examples/python/web/fastapi/main.py](../../examples/python/web/fastapi/main.py) | Компиляция Python |
| [examples/python/web/fastapi/middleware_app.py](../../examples/python/web/fastapi/middleware_app.py) | Компиляция Python |
| [examples/python/web/fastapi/minimal.py](../../examples/python/web/fastapi/minimal.py) | Компиляция Python |
| [examples/python/web/fastapi/test_async.py](../../examples/python/web/fastapi/test_async.py) | Компиляция Python |
| [examples/python/web/fastapi/test_auth.py](../../examples/python/web/fastapi/test_auth.py) | Компиляция Python |
| [examples/python/web/fastapi/test_database.py](../../examples/python/web/fastapi/test_database.py) | Компиляция Python |
| [examples/python/web/fastapi/test_dependencies.py](../../examples/python/web/fastapi/test_dependencies.py) | Компиляция Python |
| [examples/python/web/fastapi/test_dependency_override.py](../../examples/python/web/fastapi/test_dependency_override.py) | Компиляция Python |
| [examples/python/web/fastapi/test_integrations.py](../../examples/python/web/fastapi/test_integrations.py) | Компиляция Python |
| [examples/python/web/fastapi/test_main.py](../../examples/python/web/fastapi/test_main.py) | Компиляция Python |
| [examples/python/web/fastapi/uploads.py](../../examples/python/web/fastapi/uploads.py) | Компиляция Python |
| [examples/python/web/flask/flask_app.py](../../examples/python/web/flask/flask_app.py) | Компиляция Python |
| [examples/python/web/flask/flask_db.py](../../examples/python/web/flask/flask_db.py) | Компиляция Python |
| [examples/python/web/flask/test_flask_app.py](../../examples/python/web/flask/test_flask_app.py) | Компиляция Python |
| [examples/python/web/flask/test_flask_db.py](../../examples/python/web/flask/test_flask_db.py) | Компиляция Python |
| [examples/systems/linux/example.sh](../../examples/systems/linux/example.sh) | bash -n |
| [examples/systems/linux/port_probe.py](../../examples/systems/linux/port_probe.py) | Компиляция Python |
| [examples/systems/linux/process.sh](../../examples/systems/linux/process.sh) | bash -n |
| [examples/tools/api-contract-lab/.dockerignore](../../examples/tools/api-contract-lab/.dockerignore) | Правила контекста учебного образа |
| [examples/tools/api-contract-lab/Dockerfile](../../examples/tools/api-contract-lab/Dockerfile) | Сборка учебного образа Docker |
| [examples/tools/api-contract-lab/app.py](../../examples/tools/api-contract-lab/app.py) | Компиляция Python |
| [examples/tools/api-contract-lab/client.mts](../../examples/tools/api-contract-lab/client.mts) | Исходник или сборочный файл учебного проекта |
| [examples/tools/api-contract-lab/compose.yaml](../../examples/tools/api-contract-lab/compose.yaml) | Compose config, postgres, app, client |
| [examples/tools/api-contract-lab/init.sql](../../examples/tools/api-contract-lab/init.sql) | SQL в учебной БД |
| [examples/tools/api-contract-lab/requirements.txt](../../examples/tools/api-contract-lab/requirements.txt) | Манифест зависимостей |
| [examples/tools/api-contract-lab/workflow-example.yml](../../examples/tools/api-contract-lab/workflow-example.yml) | Разбор YAML, workflow GitHub |
| [examples/tools/compose-and-github-actions/.dockerignore](../../examples/tools/compose-and-github-actions/.dockerignore) | Правила контекста учебного образа |
| [examples/tools/compose-and-github-actions/Dockerfile](../../examples/tools/compose-and-github-actions/Dockerfile) | Сборка учебного образа Docker |
| [examples/tools/compose-and-github-actions/app.py](../../examples/tools/compose-and-github-actions/app.py) | Компиляция Python |
| [examples/tools/compose-and-github-actions/compose.yaml](../../examples/tools/compose-and-github-actions/compose.yaml) | Compose config, app, postgres |
| [examples/tools/compose-and-github-actions/requirements.txt](../../examples/tools/compose-and-github-actions/requirements.txt) | Манифест зависимостей |
| [examples/tools/compose-and-github-actions/test_app.py](../../examples/tools/compose-and-github-actions/test_app.py) | Компиляция Python |
| [examples/tools/compose-and-github-actions/workflow-example.yml](../../examples/tools/compose-and-github-actions/workflow-example.yml) | Разбор YAML, workflow GitHub |
| [examples/tools/compose-site/.dockerignore](../../examples/tools/compose-site/.dockerignore) | Правила контекста учебного образа |
| [examples/tools/compose-site/Dockerfile](../../examples/tools/compose-site/Dockerfile) | Сборка учебного образа Docker |
| [examples/tools/compose-site/compose.yaml](../../examples/tools/compose-site/compose.yaml) | Compose config, gateway, catalog, help |
| [examples/tools/compose-site/gateway.conf](../../examples/tools/compose-site/gateway.conf) | Конфигурация шлюза, оба HTTP-маршрута |
| [examples/tools/compose-site/pages/catalog/message.txt](../../examples/tools/compose-site/pages/catalog/message.txt) | Содержимое HTTP-ответа учебного сервиса |
| [examples/tools/compose-site/pages/help/message.txt](../../examples/tools/compose-site/pages/help/message.txt) | Содержимое HTTP-ответа учебного сервиса |
| [examples/tools/docker-basics/.dockerignore](../../examples/tools/docker-basics/.dockerignore) | Правила контекста учебного образа |
| [examples/tools/docker-basics/Dockerfile](../../examples/tools/docker-basics/Dockerfile) | Сборка учебного образа Docker |
| [examples/tools/docker-basics/compose.yaml](../../examples/tools/docker-basics/compose.yaml) | Compose config, web |
| [examples/tools/docker-basics/message.txt](../../examples/tools/docker-basics/message.txt) | Содержимое HTTP-ответа учебного сервиса |
| [examples/tools/docker-build-context/.dockerignore](../../examples/tools/docker-build-context/.dockerignore) | Правила контекста учебного образа |
| [examples/tools/docker-build-context/compose.yaml](../../examples/tools/docker-build-context/compose.yaml) | Compose config, app |
| [examples/tools/docker-build-context/dockers/Dockerfile](../../examples/tools/docker-build-context/dockers/Dockerfile) | Сборка учебного образа Docker |
| [examples/tools/docker-build-context/dockers/compose.yaml](../../examples/tools/docker-build-context/dockers/compose.yaml) | Compose config, app |
| [examples/tools/docker-build-context/main.py](../../examples/tools/docker-build-context/main.py) | Компиляция Python |
| [examples/tools/git/conflicts.sh](../../examples/tools/git/conflicts.sh) | bash -n |
| [examples/tools/git/history.sh](../../examples/tools/git/history.sh) | bash -n |
| [examples/tools/git/remotes.sh](../../examples/tools/git/remotes.sh) | bash -n |
| [examples/tools/git/workflow.sh](../../examples/tools/git/workflow.sh) | bash -n |
| [examples/tools/http-json/item.json](../../examples/tools/http-json/item.json) | Разбор JSON |
| [examples/typescript/http-client/client.mts](../../examples/typescript/http-client/client.mts) | Исходник или сборочный файл учебного проекта |

</details>

<details>
<summary>Иллюстрации и выбор языка · 27</summary>

| Файл | Проверка |
| --- | --- |
| [docs/README.md](../../docs/README.md) | 1 як., 14 ссыл. |
| [docs/assets/asyncio-waits.gif](../../docs/assets/asyncio-waits.gif) | GIF 640 × 524, 9 кадр. |
| [docs/assets/big-o-growth.svg](../../docs/assets/big-o-growth.svg) | SVG, XML и viewBox 0 0 560 320 |
| [docs/assets/csharp-shipping-fee-en.svg](../../docs/assets/csharp-shipping-fee-en.svg) | SVG, XML и viewBox 0 0 900 340 |
| [docs/assets/csharp-shipping-fee-ru.svg](../../docs/assets/csharp-shipping-fee-ru.svg) | SVG, XML и viewBox 0 0 900 340 |
| [docs/assets/csharp-xunit-test-en.svg](../../docs/assets/csharp-xunit-test-en.svg) | SVG, XML и viewBox 0 0 312 308 |
| [docs/assets/csharp-xunit-test-ru.svg](../../docs/assets/csharp-xunit-test-ru.svg) | SVG, XML и viewBox 0 0 312 308 |
| [docs/assets/fastapi-note-transaction-en.svg](../../docs/assets/fastapi-note-transaction-en.svg) | SVG, XML и viewBox 0 0 312 302 |
| [docs/assets/fastapi-note-transaction-ru.svg](../../docs/assets/fastapi-note-transaction-ru.svg) | SVG, XML и viewBox 0 0 312 302 |
| [docs/assets/fastapi-override-restoration.gif](../../docs/assets/fastapi-override-restoration.gif) | GIF 640 × 545, 5 кадр. |
| [docs/assets/git-merge-rebase.gif](../../docs/assets/git-merge-rebase.gif) | GIF 640 × 526, 3 кадр. |
| [docs/assets/git-restore-staged.gif](../../docs/assets/git-restore-staged.gif) | GIF 640 × 536, 5 кадр. |
| [docs/assets/go-request-cancellation.gif](../../docs/assets/go-request-cancellation.gif) | GIF 640 × 534, 4 кадр. |
| [docs/assets/go-worker-shutdown-en.svg](../../docs/assets/go-worker-shutdown-en.svg) | SVG, XML и viewBox 0 0 312 386 |
| [docs/assets/go-worker-shutdown-ru.svg](../../docs/assets/go-worker-shutdown-ru.svg) | SVG, XML и viewBox 0 0 312 386 |
| [docs/assets/language-toolchains-en.svg](../../docs/assets/language-toolchains-en.svg) | SVG, XML и viewBox 0 0 320 449 |
| [docs/assets/language-toolchains-ru.svg](../../docs/assets/language-toolchains-ru.svg) | SVG, XML и viewBox 0 0 320 449 |
| [docs/assets/python-list-copy.gif](../../docs/assets/python-list-copy.gif) | GIF 640 × 464, 3 кадр. |
| [docs/assets/redis-streams-ack.gif](../../docs/assets/redis-streams-ack.gif) | GIF 640 × 409, 3 кадр. |
| [docs/assets/redis-watch-conflict.gif](../../docs/assets/redis-watch-conflict.gif) | GIF 640 × 467, 4 кадр. |
| [docs/assets/sql-joins.svg](../../docs/assets/sql-joins.svg) | SVG, XML и viewBox 0 0 760 290 |
| [docs/assets/sql-users-orders-en.svg](../../docs/assets/sql-users-orders-en.svg) | SVG, XML и viewBox 0 0 312 342 |
| [docs/assets/sql-users-orders-ru.svg](../../docs/assets/sql-users-orders-ru.svg) | SVG, XML и viewBox 0 0 312 342 |
| [docs/assets/sqlalchemy-n-plus-one.gif](../../docs/assets/sqlalchemy-n-plus-one.gif) | GIF 640 × 696, 4 кадр. |
| [docs/assets/sqlalchemy-savepoint.gif](../../docs/assets/sqlalchemy-savepoint.gif) | GIF 640 × 619, 4 кадр. |
| [docs/assets/sqlalchemy-select-count.svg](../../docs/assets/sqlalchemy-select-count.svg) | SVG, XML и viewBox 0 0 520 292 |
| [docs/assets/transactional-outbox-retry.gif](../../docs/assets/transactional-outbox-retry.gif) | GIF 640 × 431, 4 кадр. |

</details>

<details>
<summary>Корневые файлы и лицензии · 7</summary>

| Файл | Проверка |
| --- | --- |
| [.gitignore](../../.gitignore) | Правила исключения Git |
| [AGENTS.md](../../AGENTS.md) | 10 як., 12 ссыл. |
| [CONTRIBUTING.md](../../CONTRIBUTING.md) | 9 як., 20 ссыл. |
| [LICENSE.md](../../LICENSE.md) | 3 як., 4 ссыл. |
| [LICENSES/CC-BY-4.0.txt](../../LICENSES/CC-BY-4.0.txt) | Лицензия, идентична исходному дереву |
| [LICENSES/MIT.txt](../../LICENSES/MIT.txt) | Лицензия, идентична исходному дереву |
| [README.md](../../README.md) | 11 як., 32 ссыл. |

</details>

<details>
<summary>Шаблоны и архив стиля · 9</summary>

| Файл | Проверка |
| --- | --- |
| [templates/README.md](../../templates/README.md) | 5 як., 14 ссыл. |
| [templates/cheat-sheet.md](../../templates/cheat-sheet.md) | 6 як., 1 ссыл. |
| [templates/guide.md](../../templates/guide.md) | 4 як., 0 ссыл. |
| [templates/procedure.md](../../templates/procedure.md) | 5 як., 0 ссыл. |
| [templates/standalone-example.md](../../templates/standalone-example.md) | 5 як., 0 ссыл. |
| [templates/ste-comparison/README.md](../../templates/ste-comparison/README.md) | 8 як., 10 ссыл. |
| [templates/ste-comparison/current.md](../../templates/ste-comparison/current.md) | 13 як., 23 ссыл. |
| [templates/ste-comparison/ste-75.md](../../templates/ste-comparison/ste-75.md) | 13 як., 23 ссыл. |
| [templates/ste-comparison/ste-80.md](../../templates/ste-comparison/ste-80.md) | 13 як., 23 ссыл. |

</details>

<details>
<summary>Настройки GitHub · 5</summary>

| Файл | Проверка |
| --- | --- |
| [.github/CODEOWNERS](../../.github/CODEOWNERS) | Правила владельцев путей |
| [.github/ISSUE_TEMPLATE/fix-material.yml](../../.github/ISSUE_TEMPLATE/fix-material.yml) | Разбор YAML, форма GitHub |
| [.github/ISSUE_TEMPLATE/new-topic.yml](../../.github/ISSUE_TEMPLATE/new-topic.yml) | Разбор YAML, форма GitHub |
| [.github/pull_request_template.md](../../.github/pull_request_template.md) | 3 як., 0 ссыл. |
| [.github/workflows/materials.yml](../../.github/workflows/materials.yml) | Разбор YAML, workflow GitHub |

</details>

<details>
<summary>Инструменты и тесты · 8</summary>

| Файл | Проверка |
| --- | --- |
| [scripts/README.md](../../scripts/README.md) | 4 як., 7 ссыл. |
| [scripts/check_materials.py](../../scripts/check_materials.py) | Компиляция Python |
| [scripts/requirements-ci.txt](../../scripts/requirements-ci.txt) | Манифест зависимостей |
| [scripts/review_signals.py](../../scripts/review_signals.py) | Компиляция Python |
| [scripts/tests/test_docker_docs.py](../../scripts/tests/test_docker_docs.py) | Компиляция Python |
| [scripts/tests/test_materials.py](../../scripts/tests/test_materials.py) | Компиляция Python |
| [scripts/tests/test_review_signals.py](../../scripts/tests/test_review_signals.py) | Компиляция Python |
| [scripts/tests/test_workflow.py](../../scripts/tests/test_workflow.py) | Компиляция Python |

</details>

<details>
<summary>Сопровождение · 19</summary>

| Файл | Проверка |
| --- | --- |
| [maintenance/README.md](../README.md) | 1 як., 8 ссыл. |
| [maintenance/plans/README.md](../plans/README.md) | 5 як., 21 ссыл. |
| [maintenance/plans/public-release.md](../plans/public-release.md) | 1 як., 2 ссыл. |
| [maintenance/plans/reader-check.md](../plans/reader-check.md) | 5 як., 7 ссыл. |
| [maintenance/reports/2026-11-07-redis-rdb-backup.md](2026-11-07-redis-rdb-backup.md) | 3 як., 3 ссыл. |
| [maintenance/reports/2026-11-08-redis-aof-backup.md](2026-11-08-redis-aof-backup.md) | 3 як., 3 ссыл. |
| [maintenance/reports/2026-11-10-history-reword-map.json](2026-11-10-history-reword-map.json) | Разбор JSON |
| [maintenance/reports/2026-11-10-publication-github.json](2026-11-10-publication-github.json) | Разбор JSON |
| [maintenance/reports/2026-11-10-safe-ci-github.json](2026-11-10-safe-ci-github.json) | Разбор JSON |
| [maintenance/reports/2026-11-10-safe-ci.md](2026-11-10-safe-ci.md) | 7 як., 17 ссыл. |
| [maintenance/reports/2026-11-10-simplification-publication.md](2026-11-10-simplification-publication.md) | 2 як., 8 ссыл. |
| [maintenance/reports/README.md](README.md) | 1 як., 17 ссыл. |
| [maintenance/reports/database-checks.md](database-checks.md) | 9 як., 21 ссыл. |
| [maintenance/reports/external-links.md](external-links.md) | 4 як., 20 ссыл. |
| [maintenance/reports/general-checks.md](general-checks.md) | 22 як., 74 ссыл. |
| [maintenance/reports/internal-links.md](internal-links.md) | 2 як., 7 ссыл. |
| [maintenance/reports/navigation-review.md](navigation-review.md) | 13 як., 32 ссыл. |
| [maintenance/reports/python-checks.md](python-checks.md) | 15 як., 53 ссыл. |
| [maintenance/reports/reference-formats.md](reference-formats.md) | 4 як., 27 ссыл. |

</details>

<details>
<summary>Восстановленные адреса · 103</summary>

| Файл | Проверка |
| --- | --- |
| [architecture/README.md](../../architecture/README.md) | 3 як., 4 ссыл. |
| [architecture/contracts.md](../../architecture/contracts.md) | 5 як., 6 ссыл. |
| [architecture/patterns/README.md](../../architecture/patterns/README.md) | 10 як., 11 ссыл. |
| [architecture/patterns/architecture-patterns.md](../../architecture/patterns/architecture-patterns.md) | 13 як., 14 ссыл. |
| [architecture/patterns/code-examples.md](../../architecture/patterns/code-examples.md) | 7 як., 8 ссыл. |
| [architecture/patterns/design-patterns.md](../../architecture/patterns/design-patterns.md) | 20 як., 21 ссыл. |
| [architecture/patterns/distributed-systems.md](../../architecture/patterns/distributed-systems.md) | 9 як., 10 ссыл. |
| [architecture/patterns/outbox-example.md](../../architecture/patterns/outbox-example.md) | 3 як., 4 ссыл. |
| [architecture/principles.md](../../architecture/principles.md) | 13 як., 14 ссыл. |
| [architecture/solid.md](../../architecture/solid.md) | 14 як., 15 ссыл. |
| [databases/README.md](../../databases/README.md) | 3 як., 4 ссыл. |
| [databases/non-relational/redis/README.md](../../databases/non-relational/redis/README.md) | 11 як., 12 ссыл. |
| [databases/non-relational/redis/aof-backup-and-restore.md](../../databases/non-relational/redis/aof-backup-and-restore.md) | 7 як., 8 ссыл. |
| [databases/non-relational/redis/backup-and-restore.md](../../databases/non-relational/redis/backup-and-restore.md) | 7 як., 8 ссыл. |
| [databases/non-relational/redis/data-and-caching.md](../../databases/non-relational/redis/data-and-caching.md) | 8 як., 9 ссыл. |
| [databases/non-relational/redis/data-lab.md](../../databases/non-relational/redis/data-lab.md) | 4 як., 5 ссыл. |
| [databases/non-relational/redis/operations.md](../../databases/non-relational/redis/operations.md) | 9 як., 10 ссыл. |
| [databases/non-relational/redis/transactions-and-messaging.md](../../databases/non-relational/redis/transactions-and-messaging.md) | 8 як., 9 ссыл. |
| [databases/non-relational/redis/transactions-lab.md](../../databases/non-relational/redis/transactions-lab.md) | 4 як., 5 ссыл. |
| [databases/relational/postgresql/README.md](../../databases/relational/postgresql/README.md) | 11 як., 12 ссыл. |
| [databases/relational/postgresql/backup-and-restore.md](../../databases/relational/postgresql/backup-and-restore.md) | 12 як., 13 ссыл. |
| [databases/relational/postgresql/backup-lab.md](../../databases/relational/postgresql/backup-lab.md) | 6 як., 7 ссыл. |
| [databases/relational/postgresql/operations.md](../../databases/relational/postgresql/operations.md) | 10 як., 11 ссыл. |
| [databases/relational/postgresql/queries.md](../../databases/relational/postgresql/queries.md) | 11 як., 12 ссыл. |
| [databases/relational/postgresql/query-lab.md](../../databases/relational/postgresql/query-lab.md) | 3 як., 4 ссыл. |
| [databases/relational/postgresql/schema-and-indexes.md](../../databases/relational/postgresql/schema-and-indexes.md) | 10 як., 11 ссыл. |
| [databases/relational/sqlite/README.md](../../databases/relational/sqlite/README.md) | 11 як., 12 ссыл. |
| [databases/relational/sqlite/backup-and-migrations.md](../../databases/relational/sqlite/backup-and-migrations.md) | 5 як., 6 ссыл. |
| [databases/relational/sqlite/backup-and-restore.md](../../databases/relational/sqlite/backup-and-restore.md) | 10 як., 11 ссыл. |
| [databases/relational/sqlite/backup-lab.md](../../databases/relational/sqlite/backup-lab.md) | 4 як., 5 ссыл. |
| [databases/relational/sqlite/migration-lab.md](../../databases/relational/sqlite/migration-lab.md) | 3 як., 4 ссыл. |
| [databases/relational/sqlite/python-and-queries.md](../../databases/relational/sqlite/python-and-queries.md) | 8 як., 9 ссыл. |
| [databases/relational/sqlite/query-lab.md](../../databases/relational/sqlite/query-lab.md) | 3 як., 4 ссыл. |
| [databases/sql/README.md](../../databases/sql/README.md) | 11 як., 12 ссыл. |
| [databases/sql/dialects-and-transactions.md](../../databases/sql/dialects-and-transactions.md) | 7 як., 8 ссыл. |
| [databases/sql/queries.md](../../databases/sql/queries.md) | 8 як., 9 ссыл. |
| [databases/sql/query-lab.md](../../databases/sql/query-lab.md) | 3 як., 4 ссыл. |
| [go/README.md](../../go/README.md) | 12 як., 13 ссыл. |
| [go/concurrency-and-testing.md](../../go/concurrency-and-testing.md) | 6 як., 7 ссыл. |
| [go/examples/concurrency-and-testing.md](../../go/examples/concurrency-and-testing.md) | 5 як., 6 ссыл. |
| [go/examples/http-json.md](../../go/examples/http-json.md) | 5 як., 6 ссыл. |
| [go/examples/language.md](../../go/examples/language.md) | 5 як., 6 ссыл. |
| [go/http-json.md](../../go/http-json.md) | 6 як., 7 ссыл. |
| [go/language.md](../../go/language.md) | 8 як., 9 ссыл. |
| [python/README.md](../../python/README.md) | 3 як., 4 ссыл. |
| [python/architecture/project-design.md](../../python/architecture/project-design.md) | 1 як., 5 ссыл. |
| [python/architecture/project-design/README.md](../../python/architecture/project-design/README.md) | 13 як., 14 ссыл. |
| [python/architecture/project-design/delivery-and-evolution.md](../../python/architecture/project-design/delivery-and-evolution.md) | 11 як., 12 ссыл. |
| [python/architecture/project-design/example.md](../../python/architecture/project-design/example.md) | 9 як., 10 ссыл. |
| [python/architecture/project-design/structure-and-decisions.md](../../python/architecture/project-design/structure-and-decisions.md) | 7 як., 8 ссыл. |
| [python/databases/sqlalchemy/README.md](../../python/databases/sqlalchemy/README.md) | 11 як., 12 ссыл. |
| [python/databases/sqlalchemy/async-and-operations.md](../../python/databases/sqlalchemy/async-and-operations.md) | 4 як., 5 ссыл. |
| [python/databases/sqlalchemy/loading-lab.md](../../python/databases/sqlalchemy/loading-lab.md) | 5 як., 6 ссыл. |
| [python/databases/sqlalchemy/models-and-transactions.md](../../python/databases/sqlalchemy/models-and-transactions.md) | 3 як., 4 ссыл. |
| [python/databases/sqlalchemy/n-plus-one.md](../../python/databases/sqlalchemy/n-plus-one.md) | 6 як., 7 ссыл. |
| [python/databases/sqlalchemy/queries.md](../../python/databases/sqlalchemy/queries.md) | 5 як., 6 ссыл. |
| [python/databases/sqlalchemy/relationship-loading.md](../../python/databases/sqlalchemy/relationship-loading.md) | 14 як., 15 ссыл. |
| [python/databases/sqlalchemy/streaming.md](../../python/databases/sqlalchemy/streaming.md) | 5 як., 6 ссыл. |
| [python/language/types/README.md](../../python/language/types/README.md) | 12 як., 13 ссыл. |
| [python/language/types/recipes.md](../../python/language/types/recipes.md) | 3 як., 4 ссыл. |
| [python/logging/structlog/README.md](../../python/logging/structlog/README.md) | 11 як., 12 ссыл. |
| [python/logging/structlog/configuration.md](../../python/logging/structlog/configuration.md) | 4 як., 5 ссыл. |
| [python/logging/structlog/context-and-web.md](../../python/logging/structlog/context-and-web.md) | 4 як., 5 ссыл. |
| [python/testing/pytest/README.md](../../python/testing/pytest/README.md) | 11 як., 12 ссыл. |
| [python/testing/pytest/configuration.md](../../python/testing/pytest/configuration.md) | 6 як., 7 ссыл. |
| [python/testing/pytest/fixtures.md](../../python/testing/pytest/fixtures.md) | 5 як., 6 ссыл. |
| [python/testing/pytest/mocking-and-async.md](../../python/testing/pytest/mocking-and-async.md) | 5 як., 6 ссыл. |
| [python/tooling/uv/README.md](../../python/tooling/uv/README.md) | 11 як., 12 ссыл. |
| [python/tooling/uv/automation.md](../../python/tooling/uv/automation.md) | 7 як., 8 ссыл. |
| [python/tooling/uv/projects.md](../../python/tooling/uv/projects.md) | 7 як., 8 ссыл. |
| [python/validation/pydantic/README.md](../../python/validation/pydantic/README.md) | 11 як., 12 ссыл. |
| [python/validation/pydantic/advanced.md](../../python/validation/pydantic/advanced.md) | 5 як., 6 ссыл. |
| [python/validation/pydantic/models.md](../../python/validation/pydantic/models.md) | 3 як., 4 ссыл. |
| [python/web/fastapi/README.md](../../python/web/fastapi/README.md) | 13 як., 14 ссыл. |
| [python/web/fastapi/authentication.md](../../python/web/fastapi/authentication.md) | 5 як., 6 ссыл. |
| [python/web/fastapi/database.md](../../python/web/fastapi/database.md) | 3 як., 4 ссыл. |
| [python/web/fastapi/dependency-overrides.md](../../python/web/fastapi/dependency-overrides.md) | 8 як., 9 ссыл. |
| [python/web/fastapi/deployment.md](../../python/web/fastapi/deployment.md) | 6 як., 7 ссыл. |
| [python/web/fastapi/http-api.md](../../python/web/fastapi/http-api.md) | 2 як., 3 ссыл. |
| [python/web/fastapi/middleware.md](../../python/web/fastapi/middleware.md) | 2 як., 3 ссыл. |
| [python/web/fastapi/recipes.md](../../python/web/fastapi/recipes.md) | 6 як., 7 ссыл. |
| [python/web/fastapi/testing-lab.md](../../python/web/fastapi/testing-lab.md) | 7 як., 8 ссыл. |
| [python/web/fastapi/testing.md](../../python/web/fastapi/testing.md) | 12 як., 13 ссыл. |
| [python/web/fastapi/uploads.md](../../python/web/fastapi/uploads.md) | 2 як., 3 ссыл. |
| [python/web/flask/README.md](../../python/web/flask/README.md) | 11 як., 12 ссыл. |
| [python/web/flask/application.md](../../python/web/flask/application.md) | 5 як., 6 ссыл. |
| [python/web/flask/configuration-and-deployment.md](../../python/web/flask/configuration-and-deployment.md) | 5 як., 6 ссыл. |
| [python/web/flask/testing.md](../../python/web/flask/testing.md) | 4 як., 5 ссыл. |
| [systems/README.md](../../systems/README.md) | 1 як., 2 ссыл. |
| [systems/linux/README.md](../../systems/linux/README.md) | 11 як., 12 ссыл. |
| [systems/linux/network-and-services.md](../../systems/linux/network-and-services.md) | 6 як., 7 ссыл. |
| [systems/linux/permissions-and-processes.md](../../systems/linux/permissions-and-processes.md) | 5 як., 6 ссыл. |
| [systems/linux/process-by-port.md](../../systems/linux/process-by-port.md) | 7 як., 8 ссыл. |
| [systems/linux/shell-and-files.md](../../systems/linux/shell-and-files.md) | 6 як., 7 ссыл. |
| [tasks/README.md](../../tasks/README.md) | 15 як., 16 ссыл. |
| [tools/README.md](../../tools/README.md) | 2 як., 3 ссыл. |
| [tools/git/README.md](../../tools/git/README.md) | 11 як., 12 ссыл. |
| [tools/git/history.md](../../tools/git/history.md) | 12 як., 13 ссыл. |
| [tools/git/remotes.md](../../tools/git/remotes.md) | 8 як., 9 ссыл. |
| [tools/git/workflow.md](../../tools/git/workflow.md) | 7 як., 8 ссыл. |
| [tools/github-pull-requests/README.md](../../tools/github-pull-requests/README.md) | 11 як., 12 ссыл. |
| [tools/github-pull-requests/merging.md](../../tools/github-pull-requests/merging.md) | 6 як., 7 ссыл. |
| [tools/github-pull-requests/review.md](../../tools/github-pull-requests/review.md) | 6 як., 7 ссыл. |

</details>
