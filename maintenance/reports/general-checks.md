# Проверки архитектуры, Go и общих инструментов

Записи сохраняют исходные даты, среды и фактические результаты.
Перенос не означает новый запуск; сверка источников учитывалась отдельно.

## HTTP и JSON — 12 ноября

[Учебный файл](../../examples/tools/http-json/item.json) отдавал `python3 -m http.server 8765 --bind 127.0.0.1 --directory examples/tools/http-json` на macOS arm64 с Python 3.14.7.
Команда `curl -i` показала HTTP/1.0 200, заголовок `Content-Type: application/json` и ожидаемое тело. Запрос с `jq -r '.name'` вывел `Book`. Отсутствующий файл вернул HTTP 404.
Прогон выполнен по [двуязычному примеру](../../docs/ru/tools/http-json.md) в Bash 3.2.57 и Zsh 5.9 с curl 8.7.1 и jq 1.7.1 Apple. Проверка обращалась только к локальному серверу.

## Docker Compose и GitHub Actions — 12 ноября

В изолированном [учебном проекте](../../docs/ru/tools/compose-and-github-actions.md) проверили `docker compose config -q` и `docker compose up --build -d --wait`.
Среда запуска — Docker Engine 29.9.3, Compose 5.7.0, Linux arm64, Python 3.14.10, Psycopg 3.3.9 и PostgreSQL 18.6.
Оба сервиса получили статус `healthy`. Запрос к `/health` вернул HTTP 200 и `{"status": "ok", "database": "compose_lab"}`.
Команда `docker compose exec -T app python -m unittest -v` завершилась с `OK`. С `LAB_FORCE_FAILURE=1` она вернула код 1 и `AssertionError: 'compose_lab' != 'intentional_failure'`. Повтор без переменной вернул `OK`.
Остановка PostgreSQL дала HTTP 503 и строку `PostgreSQL is unavailable` в журнале. Повторный `up -d --wait` восстановил HTTP 200.
Команда `down` сохранила учебный том. Команда `down --volumes` удалила его.

`actionlint` 1.7.12 проверил исходный [учебный workflow](../../examples/tools/compose-and-github-actions/workflow-example.yml) и его копию по пути `.github/workflows/postgres-test.yml` во временном репозитории.
Команду теста из workflow выполнили отдельно в новом venv на macOS arm64 с Python 3.14.7. PostgreSQL 18.6 работал в отдельном контейнере со случайным локальным портом.
Значения переменной `LAB_FORCE_FAILURE` 0, 1 и 0 дали `OK`, ошибку с кодом 1 и `OK`.
Ручной запуск, порт контейнера и порядок чтения журнала сверили с официальной документацией. Выполнение на GitHub-hosted runner остаётся непроверенным. [Docker Compose Quickstart](https://docs.docker.com/compose/gettingstarted/) · [Сервис PostgreSQL в GitHub Actions](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) · [Ручной запуск](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) · [Журналы GitHub Actions](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs).

## Go context — 12 ноября

На Go 1.27.1 darwin/arm64 выполнили `GOTOOLCHAIN=local go run ./examples/go/context/main.go`.
[Пример](../../docs/ru/go/context.md) подтвердил тело успешного ответа `ok`, ошибку `context.DeadlineExceeded` после тайм-аута и `context.Canceled` после явной отмены начатого запроса.
Программа открывала только локальный порт. Требование Go 1.16 для `io.ReadAll` сверили с [примечаниями к выпуску](https://go.dev/doc/go1.16). Эту версию отдельно не запускали.

## Архитектура и Python-пакет — 6 и 8 ноября

Среда: macOS arm64, Python 3.14.7, SQLite 3.53.4.
8 ноября из Markdown извлечены и выполнены восемь полных программ:
`invariants.py`, `solid-contract.py`, `solid-srp.py`, `solid-ocp.py`, `shipping-patterns.py`, `observer-pattern.py`, `command-pattern.py`, `outbox.py`.
Все процессы дали код 0; встроенные assertions прошли.
Шесть мини-примеров `design-patterns.md` также дали код 0.

| Материал | Проверенные результаты |
| --- | --- |
| [Контракты](../../docs/ru/architecture/contracts.md) | Резерв, отказ при 0/True/нехватке, недопустимый остаток; цена 2400, отказ количества 0, подстановка и неправильная ошибка |
| [Доставка, Observer, Command](../../docs/ru/architecture/patterns/code-examples.md) | Тарифы, единицы, округление; результат обёртки и аудит; порядок/отписка/ошибка слушателя; повтор команды и конфликт ID |
| [Outbox](../../docs/ru/architecture/patterns/outbox-example.md) | Rollback обеих записей при UNIQUE-отказе; дубликат публикации после смоделированного сбоя |

БД Outbox находилась в памяти; брокер заменён списком, worker один.
Настоящие процессные сбои, диск, надёжный аудит, сеть и конкурентные вызовы не проверялись.
Деревья архитектуры показывают возможную реализацию; они не являются запущенными приложениями.

[Пакет catalog_demo](../../docs/ru/python/architecture/project-design/example.md) проверен 6 и 8 ноября в отдельном окружении.
Использованы uv 0.12.13, Pydantic 2.14.3, pydantic-settings 2.16.2, pytest 9.2.0.
`uv sync --group dev` и `python -m pytest -q` дали 9 passed.
`python -m catalog_demo book` дал `book: Python guide`.
Вызовы с unknown и пустым SKU дали код 2; неизвестный `CATALOG_DEMO_ENVIRONMENT` отклонён до сборки приложения.
Иллюстративные миграции рабочей БД и production-поставка не выполнялись.
Python 3.14, PyPA и Pydantic Settings сверены с первичными источниками 6 и 8 ноября.

## Go — 6, 8 и 10 ноября

Среда запусков: Go 1.27.1 darwin/arm64, только стандартная библиотека, временные caches, `GOTOOLCHAIN=local`.
Файлы [полных примеров](../../docs/ru/go/examples/language.md) извлечены из Markdown.
6 и 8 ноября прошли `go test`, `go vet`, `go test -race`; 8 ноября использован `-count=1`.
Восемь исходных тестовых функций проверили ввод, данные, HTTP и конкурентность.
`go run ./cmd/demo` дал `Alice Doe (30)` и `true`.
Пять отдельных карточек и HTTP-тест подтвердили заявленные выводы, HTTP 200 и имя Alice.

Проверены порядок строк, пустой ввод, неверные workers, уже отменённый context и конкурентный счётчик.
HTTP Recorder проверил JSON, метод, Content-Type и ограничение тела.
10 ноября HTTP и workers отдельно собраны в двух новых папках с одним go.mod и только своими файлами.
`go test -count=1 ./...` прошёл в обеих папках; `GOENV=off`, caches отдельные, toolchain не скачивался.
При ревью публикации 10 ноября все три самостоятельных Go-примера также прошли `go test ./...`.

TLS, proxy, реальный HTTP-сервер и нагрузка не проверялись.
Детерминированная отмена посреди операции и полный подсчёт утечек отсутствуют.
Race detector проверил выполненные пути; он не доказывает отсутствие всех гонок и deadlock.
Спецификация, stdlib и release notes Go 1.27 сверены 6 и 8 ноября; остальные patch-версии не запускались.

## Git — 6 и 8 ноября

Среда: Git 2.55.0, macOS, Bash 3.2.57.
Четыре скрипта выполнялись на синтетических данных во временных репозиториях с локальным bare remote.
Глобальная конфигурация, подписи и hooks изолированы; внешнего push не было.

| Команда | Результат |
| --- | --- |
| `bash workflow.sh` | `workflow OK`: tracked/untracked восстановлены, ignored не попал в stash |
| `bash history.sh` | `history OK`: index/worktree, soft/mixed/hard, reflog и revert |
| `bash conflicts.sh` | `conflicts OK`: реальные merge/rebase-конфликты; abort восстановил состояние, continue завершил операцию |
| `bash remotes.sh` | `remote lease and cleanup OK`: устаревший lease отклонён до и после fetch; коммит второй копии сохранён |

[Полные сценарии](../../docs/ru/tools/git/README.md#быстрый-поиск) доступны из карточек Git.
Отдельные пробы 6 ноября проверили новый staged-файл, источник restore, stash `--index`, новый ID после amend и revert abort/continue.
Подтверждены потеря мешающего untracked-пути при hard reset и отказ `branch -d` после squash.
Успешный `branch -d` относительно upstream сам по себе не доказал включение в main.
8 ноября локальная main с дополнительным коммитом прошла `merge --ff-only origin/main`.
При этом `origin/main..main` показал один неопубликованный коммит; cleanup требует проверки опубликованного результата.
Руководства и release notes Git v2.55.0 сверены отдельно.
GitHub-рецепты проверены по документации и `gh 2.100.0 --help`; серверные права этими учебными запусками не проверялись.

## Bash, файлы и процессы — 6 и 8 ноября

Среда: macOS, Bash 3.2.57, Python 3.14.7; только собственные временные файлы и процессы.
`bash example.sh` дал `files OK`: копирование, архив, восстановление и gzip сохранили содержимое.
`bash process.sh` дал `process OK`: готовность подтверждена до TERM, статус -15, выполнен wait.
6 ноября прошли 100 последовательных запусков и 100 запусков с четырьмя параллельными проверками.
Отдельно подтверждены отказ готовности и очистка после исключения перед штатным TERM.

Карточки chmod/find/grep/cp подтвердили 600/700, имена с пробелом и переводом строки, раздельные stdout/stderr.
`cp -i` с ответом n сохранил назначение; BSD cp вернул 1, переносимый код отказа не заявлен.
Свой HTTP-сервер на 127.0.0.1 и curl 8.7.1 дали код 0 для 200 и код 22 для 422.
`--fail-with-body` сохранил оба тела ответа; сервер остановлен после проверки.
Эти прогоны не подтверждают GNU-флаги, Linux procps, systemd, APT/DNF, SSH или административные изменения.

## Linux: владелец порта — 6 ноября

[port_probe.py](../../docs/ru/systems/linux/process-by-port.md#самостоятельный-учебный-пример) выполнен в одноразовом Debian 13.6 arm64 контейнере без внешней сети.
Среда: Linux 7.0.14-linuxkit, iproute2 6.15.0, procps-ng 4.0.4, util-linux 2.41.5, Python 3.13.5.
Пример также прошёл под UID 65534 без sudo.
Создан только собственный loopback-сокет с портом ОС; чужие процессы не останавливались.

Пять временных `unittest` с `-W error` проверили точный выбор 8000 без 18000, PID/ps и исчезновение listener.
Проверены скрытые сведения чужого UID, связанный/несвязанный UDP, TCP ESTAB и TCP без LISTEN.
Без дополнительных capabilities `nsenter --net` дал `Operation not permitted`.
Четыре проверки namespace подтвердили: другая сеть скрывает listener; общая сеть без общих PID показывает сокет без владельца.
Общие network/PID namespace вернули PID владельца.
Рецензент независимо повторил полный пример и все девять проверок.
Контейнеры не использовали host network, опубликованные порты, host mounts или дополнительные привилегии; после проверки контейнеры удалены.

Успешный nsenter, SELinux/AppArmor, hidepid, IPv6 и рабочие firewall/NAT/proxy не проверялись.
8 и 10 ноября Linux runtime не повторялся; проверка на macOS ограничивалась синтаксисом и переносимыми сценариями.
Удобство поиска и понимание текста с реальными читателями не измерялись.
