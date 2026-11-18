# Проверки архитектуры, языков и общих инструментов

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
Ручной запуск, порт контейнера и порядок чтения журнала сверили с официальной документацией. [Docker Compose Quickstart](https://docs.docker.com/compose/gettingstarted/) · [Сервис PostgreSQL в GitHub Actions](https://docs.github.com/en/actions/tutorials/use-containerized-services/create-postgresql-service-containers) · [Ручной запуск](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) · [Журналы GitHub Actions](https://docs.github.com/en/actions/how-tos/monitor-workflows/use-workflow-run-logs).

### Проверка на GitHub

Полные журналы трёх запусков выгрузили 18 ноября 2026 года перед удалением учебного репозитория. [Архив сохранён в истории Git](https://github.com/IAMN1/devrefsnap/tree/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab). Исходные даты проверок сохранены.

В приватном учебном репозитории установили исходный workflow по пути `.github/workflows/postgres-test.yml`. Оба запуска выполнены на коммите `f72cc81` с Ubuntu 24.04, Python 3.14.10 и сервисом PostgreSQL 18.6.

- `gh workflow run postgres-test.yml --ref main -f fail_test=true` дал отказ в шаге `Run database test`. Журнал содержит `test_reports_current_database`, `AssertionError: 'compose_lab' != 'intentional_failure'` и код 1. [Отказ](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/43265099266.log)
- Новый запуск с `-f fail_test=false` прошёл. В том же шаге видны `test_reports_current_database … ok` и `OK`. [Успешный повтор](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/43265365559.log)

## Контракт FastAPI и TypeScript — 12 ноября

В [сквозном примере](../../docs/ru/tools/api-contract-lab.md) одна команда `docker compose run --build --rm client` компилирует TypeScript и проверяет реальный HTTP-ответ FastAPI с PostgreSQL. Код клиента проверяет статус, форму JSON и учебные значения.

Локальная среда — Docker Engine 29.9.3 на Linux arm64, Compose 5.7.0, Python 3.14.10, FastAPI 0.162.0, Uvicorn 0.54.0, Psycopg 3.3.9, PostgreSQL 18.6, Node.js 26.8.2 и TypeScript 6.0.3. `docker compose config -q` и `actionlint` 1.7.12 прошли. В отдельных копиях клиент вернул код 1 при HTTP 200 со строковым `id` и при HTTP 200 вместо 404 для отсутствующей книги. Обе схемы отрисовали в Mermaid 11.17.2.

Локальный прогон на пустом томе вывел обе строки `OK GET` и завершился с кодом 0. После `down --volumes` проверили отсутствие контейнеров, сетей и томов тестовых проектов.

На GitHub запустили образец `.github/workflows/api-contract.yml` с коммита `a1eb3e8` приватного учебного репозитория. Файлы и workflow побайтово совпадают с примером справочника. Команда на Ubuntu 24.04 вывела `OK GET /books/1 -> 200 The Hobbit` и `OK GET /books/999 -> 404 Book not found`. Шаг очистки удалил сеть и том `books-data`. [Запуск сквозной проверки](https://github.com/IAMN1/devrefsnap/blob/2b164491a2c880fc69484d78c73c6ad777d8f2dd/maintenance/reports/github-actions-lab/43265665681.log)
Ветки диагностики и очистки сквозного workflow после отказа на GitHub отдельно не запускались. Два отказа контракта воспроизвели локально.

## Go context — 12 ноября

На Go 1.27.1 darwin/arm64 выполнили `GOTOOLCHAIN=local go run ./examples/go/context/main.go`.
[Пример](../../docs/ru/go/context.md) подтвердил тело успешного ответа `ok`, ошибку `context.DeadlineExceeded` после тайм-аута и `context.Canceled` после явной отмены начатого запроса.
Программа открывала только локальный порт. Требование Go 1.16 для `io.ReadAll` сверили с [примечаниями к выпуску](https://go.dev/doc/go1.16). Эту версию отдельно не запускали.

## Основы C, C# и C++ — 12 ноября 2026

Команды сборки и запуска выполнили на macOS 27.2.1 arm64. Результаты сборки хранили во временных каталогах. Архив .NET SDK распаковали отдельно после проверки SHA-512 по метаданным Microsoft.

| Материал | Среда и команды | Результат |
| --- | --- | --- |
| [C](../../docs/ru/c/README.md#первый-запуск) | Apple Clang 21.0.0 (`clang-2100.4.1.1`), `clang -std=c17 -Wall -Wextra -pedantic` | Код 0 и `Count: 2`. Отдельно проверили совпадение с порогом, подсчёт всех и отсутствие подходящих элементов, нулевую длину. |
| [C#](../../docs/ru/csharp/README.md#первый-запуск) | .NET SDK 10.0.404, runtime 10.0.15, `dotnet build` и `dotnet run --no-build` с одним `--artifacts-path` | Сборка с 0 предупреждений и 0 ошибок. Без аргументов вывод `Count: 2`, с аргументом `5` — `Count: 1`. Проверили оба предела `int`. Неверный формат, число вне диапазона и два аргумента дали код 2 и сообщение в stderr. |
| [C++](../../docs/ru/cpp/README.md#первый-запуск) | Apple Clang 21.0.0, `clang++ -std=c++20 -Wall -Wextra -pedantic` | Код 0 и `Count: 2`. Отдельно проверили совпадение с порогом, подсчёт всех и отсутствие подходящих элементов, пустой вектор. Вызов `at(size())` выбросил `std::out_of_range`. |

Граничные случаи C и C++ проверили во временных программах с исходниками примеров и флагами `-Werror -fsanitize=address,undefined -fno-sanitize-recover=all`. Все проверки завершились с кодом 0. Команды, фрагменты кода и ожидаемый вывод совпадают в русских и английских страницах.

В отдельном окружении с Python 3.14.7 и зависимостями из `scripts/requirements-ci.txt` статическая проверка прошла без ошибок. Все 27 тестов проверяющего кода прошли.

Режимы языка и команды сверили с руководствами и примечаниями к выпускам. Выбор C# 14 следует из целевой платформы `net10.0`. [Руководство Clang 21](https://releases.llvm.org/21.1.0/tools/clang/docs/UsersManual.html) · [Примечания Clang 21](https://releases.llvm.org/21.1.0/tools/clang/docs/ReleaseNotes.html) · [Версии C#](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-versioning#defaults) · [Примечания .NET 10.0.15](https://github.com/dotnet/core/blob/main/release-notes/10.0/10.0.15/10.0.15.md).

Граница прогона — macOS arm64, Apple Clang 21.0.0 и .NET SDK 10.0.404. Сборки на Linux и Windows, GCC и MSVC остались за пределами прогона.

### Расширенные справочники

Для каждого языка добавили страницы синтаксиса, инструментов и практик. Обе языковые версии используют общий проект с тестами. Официальные руководства, версии библиотек и примечания к выпускам указаны рядом с соответствующими рецептами.

| Проект | Среда и выполненные команды | Фактический результат |
| --- | --- | --- |
| [Парсер порта на C](../../docs/ru/c/tooling-and-testing.md#tests) | Apple Clang 21.0.0, CMake/CTest 3.31.12, GNU Make 3.81. `cmake -S/-B`, `cmake --build`, `ctest --output-on-failure --no-tests=error`. CMake загрузил Unity 2.7.0 через `FetchContent` с проверкой SHA-256. | CTest 1/1, Unity 6/6. Повтор с ASan и UBSan прошёл. CLI вывел `Port: 8080`. Значение `65536` и отсутствие аргумента дали код 1 и сообщение в stderr. |
| [Расчёт доставки на C#](../../docs/ru/csharp/tooling-and-testing.md#tests) | .NET SDK 10.0.404, runtime 10.0.15, xUnit v3 3.2.2, адаптер 3.1.5, Microsoft.NET.Test.Sdk 18.0.1. `dotnet restore`, `dotnet build --no-restore`, `dotnet test --no-build` с общим каталогом артефактов. | Сборка с 0 предупреждений и 0 ошибок. Все 5 тестов прошли. Фильтр неверного ввода выполнил 1 тест. Проверены суммы по обе стороны порога, сам порог и исключение для отрицательного значения. |
| [Подсчёт баллов на C++](../../docs/ru/cpp/tooling-and-testing.md#run-the-lab) | Apple Clang 21.0.0, CMake/CTest 3.31.12, vcpkg 2026.05.25, triplet `arm64-osx`, pkgconf 2.5.1, GoogleTest 1.17.0#2. Конфигурация CMake с toolchain vcpkg, сборка и CTest. Порты собраны при `VCPKG_BINARY_SOURCES=clear`. | CTest 6/6. Для порога 60 и трёх баллов CLI вывел `2 of 3`. Пустой набор дал `0 of 0`. Неверное целое, выход за диапазон и отсутствие порога дали код 2. |

Отдельные сборки C и C++ в режиме Release с `BUILD_TESTING=OFF` прошли без тестовых зависимостей. CLI C принял верхнюю границу 65535 и отклонил 65536. CLI C++ подтвердил подсчёт, пустой набор и отказ для балла 101.

Скомпилировали и выполнили пять фрагментов C и одиннадцать фрагментов C++ из страниц синтаксиса и практики. Сборка консольного проекта C++ с ASan и UBSan вывела `2 of 3` без диагностики. Команды первого запуска всех трёх языков повторили прямо из Markdown.

В C# отдельно проверили установку `Newtonsoft.Json` 13.0.4, список пакетов, восстановление по `NuGet.Config` и повтор с `--locked-mode`. Локальный манифест восстановил `dotnet-ef` 10.0.0. Выполнили фрагменты синтаксиса и пример внедрения через конструктор с предупреждениями как ошибками. Запрос с провайдером `Microsoft.EntityFrameworkCore.Sqlite` 10.0.15 вернул 20 открытых заказов с нужными полями и порядком из базы SQLite в памяти.

Проверили зеркальные пути и совпадение команд, кода и ожидаемого вывода на 24 страницах. Десять схем отрисовались в Mermaid 11.17.2 через WebKit. Проверили отображение обеих версий SVG со схемой сборки и графиком стоимости доставки. Порог графика соответствует условию в `ShippingFee.cs` и тестам для 4 999 и 5 000 центов.

Прогоны ограничены macOS arm64 и указанными инструментами. Минимальные версии инструментов, альтернативные менеджеры пакетов и остальные области применения сверили с документацией. Сборка под Linux и Windows, работа с оборудованием и интеграция с внешними сервисами остались за пределами лабораторий.

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

## TypeScript и FastAPI — 12 ноября

Скомпилировали [учебный клиент](../../docs/ru/typescript/README.md) через TypeScript 6.0.3 с `--strict --noEmitOnError` в отдельный каталог. Проверили полученный модуль командой `node --check`.
На Node.js 26.8.2 и npm 11.19.1 клиент получил `200` от локального FastAPI 0.162.0 с Uvicorn 0.54.0 и вывел `Привет`.
Отдельный локальный сервер вернул ответы для проверки отказов. Числовой `message`, пустой объект и `null` дали ошибку проверки структуры. Некорректный JSON дал ошибку разбора. При статусе `404` клиент сообщил об HTTP-ошибке до разбора тела. Во всех случаях отказа процесс завершился с кодом 1.
Клиент проверен в Node.js. [Руководство TypeScript](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) · [Node.js `fetch`](https://nodejs.org/download/release/v26.8.2/docs/api/globals.html#fetch).

## Big O — 12 ноября

На Python 3.14.7 запустили [пример подсчёта операций](../../docs/ru/algorithms/README.md#big-o). Для `n = 4, 8, 16` он вывел линейные числа 4, 8, 16 и квадратичные 16, 64, 256.
Счётчики дополнительно проверили на `range`, списках и повторяющихся значениях для размеров от 0 до 32. Точки на общей диаграмме сверены с выводом. Пример считает итерации тела цикла. [Определение Big O в NIST](https://www.nist.gov/dads/HTML/bigOnotation.html).

## Повторные проверки — 15 ноября 2026

Результаты перенесены из аудита публичного справочника с исходной датой. Перенос не означает новый запуск.

| Сценарий | Среда и фактический результат |
| --- | --- |
| [HTTP и JSON](../../docs/ru/tools/http-json.md) | Python 3.14.7, jq 1.7.1. Локальный сервер на свободном порту `127.0.0.1` вернул HTTP 200. `curl -i` показал заголовки и тело, `curl -I` — заголовки без тела. `jq -r '.name'` вывел `Book` |
| [Первый C++20-пример](../../docs/en/cpp/README.md#first-run) | Apple Clang 21 собрал пример с результатом `Count: 2` |
| [Учебная история Git](../../docs/ru/tools/git/history.md) | Git 2.55.0: сценарий завершился с `history OK`. Отдельная проба merge/rebase подтвердила двух родителей merge и новый SHA коммита после rebase на локальной ветке |
| [Go context](../../examples/go/context/main.go) | Go 1.27.1 выполнил три исхода локальных HTTP-запросов. Проверены успешный ответ, тайм-аут и отмена; в сценарии отмены наблюдали результат клиента и завершение обработчика |
| [Outbox](../../examples/architecture/outbox.py) | Python 3.14: имитация сбоя после первой публикации оставила `sent = 0`. Повтор дал две публикации одного события с тем же идентификатором; публикацию заменял список |

Локальная справка GitHub CLI подтвердила `gh run view RUN_ID --log-failed`; реальный журнал Actions в этом проходе не запрашивали. Нового сквозного прогона CI, PostgreSQL или контейнерных пространств имён в рамках аудита не было. Для Outbox имитировали сбой в учебном коде; реальные процессные сбои и брокер не проверялись.

[Проверки Python](python-checks.md#проверки-примеров-для-gif--15-ноября-2026) · [Проверки БД](database-checks.md#проверки-иллюстраций--15-ноября-2026) · [Навигация и просмотр GIF](navigation-review.md#публичный-вход-и-gif--15-ноября-2026).
