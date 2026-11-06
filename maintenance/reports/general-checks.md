# История проверки общих материалов

Записи перенесены из читательских страниц.
Даты, версии окружений и результаты ниже описывают проведённые проверки.
Перенос не означает повторное выполнение примеров.

## `architecture/README.md`

Исходная страница: [architecture/README.md](../../architecture/README.md).

> Паспорта подробных страниц отдельно указывают источники, выполненные сценарии и границы проверки.

## `architecture/contracts.md`

Исходная страница: [architecture/contracts.md](../../architecture/contracts.md).

> **Сверено с документацией:** 2026-11-06: Python 3.14, PEP 544; первичные источники внизу

> **Выполнено:** 2026-11-06: Python 3.14.7, оба полных примера; сценарии перечислены ниже

> **Границы:** Память, один поток, синтетические данные; без БД, сети и статического анализатора

> Проверены успешный резерв, `0`, `True`, нехватка и недопустимый начальный остаток.

> Этот пример не проверяет конкурентный резерв.

> Проверены цена `2400`, отказ количества `0`, успешная подстановка и обнаружение неправильной ошибки.

> Здесь выполнены поведенческие проверки.
> Статический анализатор не запускался.

## `architecture/patterns/README.md`

Исходная страница: [architecture/patterns/README.md](../../architecture/patterns/README.md).

> **Сверено с источниками:** 2026-11-06: GoF, Cockburn, Fowler/Bogard, Microsoft и Python 3.14; ссылки на подробных страницах

> **Выполнено:** [Паттерны кода: дата, версии, сценарии](../../architecture/patterns/code-examples.md#границы-примеров); [Outbox: паспорт](../../architecture/patterns/distributed-systems.md)
> **Границы:** Локальные учебные примеры; сеть, процессные сбои, нагрузка и конкуренция не проверялись

## `architecture/patterns/architecture-patterns.md`

Исходная страница: [architecture/patterns/architecture-patterns.md](../../architecture/patterns/architecture-patterns.md).

> **Сверено с источниками:** 2026-11-06, Cockburn, Bogard, Fowler / Lewis и Microsoft Azure Architecture Center; ссылки рядом с темами

> **Выполнено:** [Полный Outbox](../../architecture/patterns/distributed-systems.md#полный-пример-outbox-и-дубликат-публикации): дата, версии и проверенные отказы указаны на подробной странице

> **Границы:** Деревья и схемы — возможные решения, не запущенные приложения и не измерения

## `architecture/patterns/code-examples.md`

Исходная страница: [architecture/patterns/code-examples.md](../../architecture/patterns/code-examples.md).

> **Сверено с документацией:** 2026-11-06: Python 3.14, [Callable](https://docs.python.org/3.14/library/collections.abc.html#collections.abc.Callable), [Decimal](https://docs.python.org/3.14/library/decimal.html), [dataclasses](https://docs.python.org/3.14/library/dataclasses.html)

> **Выполнено:** 2026-11-06, Python 3.14.7: доставка, Observer и Command; успешные сценарии и перечисленные отказы, а также короткие продолжения из шпаргалки

> Проверены два тарифа.
> Проверен перевод граммов в килограммы.
> Проверено явное округление вверх до цента.
> Проверены сохранение результата обёрткой и запись аудита.
> Проверены три сценария отказа.

> Проверены два слушателя, порядок, отписка и прерывание рассылки при исключении.

> Проверены резервирование и успешный повтор.
> Проверены невалидное количество, недостаточный остаток и конфликт ID.

> **Не проверяется этими примерами:** Сеть/реальный SDK, потоки, падение процесса, надёжный аудит, доставка и хранение команд

## `architecture/patterns/design-patterns.md`

Исходная страница: [architecture/patterns/design-patterns.md](../../architecture/patterns/design-patterns.md).

> **Сверено с документацией:** 2026-11-06: Python 3.14 (`Callable`, `Decimal`, `dataclass`); намерения паттернов — GoF

> **Выполнено:** 2026-11-06, Python 3.14.7: доставка, Observer и Command; успешные сценарии и перечисленные отказы, а также короткие продолжения из шпаргалки

> **Границы:** Синтетические данные и стандартная библиотека; без сетевого SDK, потоков и надёжного аудита/доставки

## `architecture/patterns/distributed-systems.md`

Исходная страница: [architecture/patterns/distributed-systems.md](../../architecture/patterns/distributed-systems.md).

> **Сверено с документацией:** 2026-11-06, Microsoft Azure Architecture Center и Python sqlite3 3.14; источники рядом с карточками

> **Выполнено:** 2026-11-06, Python 3.14.7 / SQLite 3.53.4: полный пример Outbox; rollback обеих записей при отказе UNIQUE и повтор публикации после смоделированного сбоя

> **Границы:** Один worker, БД в памяти, список вместо брокера; сеть, процессный сбой, диск и конкуренция не проверены

> Пример не проверяет настоящий процессный сбой или диск.

## `architecture/principles.md`

Исходная страница: [architecture/principles.md](../../architecture/principles.md).

> Концепции сверены с первичными источниками 2026-11-06.
> Версии Python и выполненные сценарии указаны в [паспорте примеров](../../architecture/contracts.md).

## `architecture/solid.md`

Исходная страница: [architecture/solid.md](../../architecture/solid.md).

> **Сверено:** 2026-11-06, Martin, Liskov/Wing, PEP 544 и документация Python 3.14. [Источники](../../architecture/solid.md#источники).

> **Выполнено:** 2026-11-06, Python 3.14.7: мини-примеры S/O и [контракт цены](../../architecture/contracts.md#подстановка-источника-цен).

> Проверки выполнены локально.

## `go/README.md`

Исходная страница: [go/README.md](../../go/README.md).

> **Сверено с документацией:** 2026-11-06, спецификация Go, документация стандартной библиотеки и release notes 1.27

> **Выполнено:** 2026-11-06, go1.27.1 darwin/arm64: 8 Go-файлов отформатированы; `go test`, `go vet`, `go test -race` и программа demo прошли. Проверки использовали временные caches, `GOTOOLCHAIN=local` и только stdlib

## `go/concurrency-and-testing.md`

Исходная страница: [go/concurrency-and-testing.md](../../go/concurrency-and-testing.md).

> Сверено 2026-11-06 с Go 1.27 и API context/sync.

> Выполнено 2026-11-06 на go1.27.1 darwin/arm64.

> Проверены порядок результата, пустой ввод, неверное число workers, уже отменённый context и конкурентный счётчик.
> `go vet` и `go test -race -count=1 ./...` успешны.

## `go/http-json.md`

Исходная страница: [go/http-json.md](../../go/http-json.md).

> Сверено 2026-11-06 с `encoding/json`, `net/http`, `httptest` Go 1.27.

> Выполнено 2026-11-06 на go1.27.1 darwin/arm64.

> Через Recorder проверены корректный и некорректный JSON, HTTP-метод, тип содержимого и ограничение тела.
> `go test`, vet и race-прогон успешны.

> Реальный сервер, TLS и нагрузочные сценарии здесь не запускались.

## `go/language.md`

Исходная страница: [go/language.md](../../go/language.md).

> Сверено 2026-11-06 с Go 1.27.

> Выполнено 2026-11-06 на go1.27.1 darwin/arm64: demo выдал ожидаемый вывод.

> Языковые тесты, gofmt, vet и race-прогон успешны.

## `systems/README.md`

Исходная страница: [systems/README.md](../../systems/README.md).

> Проверка переносимой команды Bash на macOS не подтверждает работу GNU-флагов, ядра Linux или systemd.

## `systems/linux/README.md`

Исходная страница: [systems/linux/README.md](../../systems/linux/README.md).

> **Сверено с документацией:** 2026-11-06, GNU Bash/Coreutils/Findutils/Grep, Linux man-pages, systemd, Debian APT и DNF

> **Исходная проверка:** 2026-11-06: переносимые учебные скрипты Bash на macOS

> **Поиск процесса по порту:** 2026-11-06: [учебный пример, версии и границы](../../systems/linux/process-by-port.md); Debian 13.6, iproute2 6.15.0, procps-ng 4.0.4, util-linux 2.41.5, Python 3.13.5

> **Остальные сценарии:** GNU-specific flags, systemd и package managers как учебные рецепты не запускались

> Поиск процесса по порту проверен в учебном Linux-контейнере; границы остальных проверок указаны ниже.

> Выполнение переносимого скрипта на macOS не считается выполнением Linux-рецепта.

## `systems/linux/network-and-services.md`

Исходная страница: [systems/linux/network-and-services.md](../../systems/linux/network-and-services.md).

> Сверка: 2026-11-06. Поиск процесса по порту проверен [отдельно](../../systems/linux/process-by-port.md).

> Поиск процесса по порту выполнен в отдельном Linux-контейнере; [сценарий и границы](../../systems/linux/process-by-port.md) указаны отдельно.

> **Операции установки не выполнялись**.

> `/proc`, GNU df/du/free здесь не проверялись запуском.
> Системные файлы не очищались.

> Остальные сетевые рецепты, службы, пакетные менеджеры, SSH и внешняя доступность приложений не тестировались.

## `systems/linux/permissions-and-processes.md`

Исходная страница: [systems/linux/permissions-and-processes.md](../../systems/linux/permissions-and-processes.md).

> Сверка: 2026-11-06. Административные команды и изменения системной конфигурации не выполнялись.

> Здесь chown/sudo и административные изменения не выполнялись.

> Проверка 2026-11-06: macOS, Bash 3.2.57, CPython 3.14.7.
> Выполнены 100 последовательных запусков и 100 запусков с четырьмя параллельными проверками.
> Во всех запусках подтверждена готовность перед TERM и получен код `-15`.
> Отдельно проверены отказ готовности и очистка после исключения перед штатным TERM.
> Чтение таблицы процессов через ps ограничено средой проверки macOS.
> Формат вывода Linux procps и жизненный цикл служб не проверялись запуском.

## `systems/linux/process-by-port.md`

Исходная страница: [systems/linux/process-by-port.md](../../systems/linux/process-by-port.md).

> **Сверено с документацией:** 2026-11-06: iproute2 6.15.0, объявление выпуска 6.15; Linux man-pages; справочники Debian trixie для ss, ps и nsenter

> **Выполнено:** 2026-11-06: Debian 13.6 arm64 в отдельном контейнере, Linux 7.0.14-linuxkit, iproute2 6.15.0, procps-ng 4.0.4, util-linux 2.41.5, Python 3.13.5

> Другие версии, firewall, рабочие службы и внешняя доступность порта здесь не проверяются.

> Успешный вход через `nsenter` в этой проверке не выполнялся; в обычном учебном контейнере подтверждён отказ по правам.

## `systems/linux/shell-and-files.md`

Исходная страница: [systems/linux/shell-and-files.md](../../systems/linux/shell-and-files.md).

> Сверка: 2026-11-06.

> Скрипт проверен на macOS с BSD-утилитами.
> Проверка охватывает переносимое подмножество и не подтверждает работу GNU/Linux.

> Варианты только для Linux/GNU здесь не выполнялись.

> Выполнен только полный скрипт с временными файлами на macOS.
> Различия GNU/BSD приведены справочно.

## `tools/README.md`

Исходная страница: [tools/README.md](../../tools/README.md).

> Действия в GitHub описаны по документации.
> Эти действия не выполнялись в аккаунте.

> Границы проверки указаны в материалах.

Статус материалов в прежнем каталоге: Git и GitHub Pull Requests — «Актуализировано».

## `tools/git/README.md`

Исходная страница: [tools/git/README.md](../../tools/git/README.md).

> **Сверено с документацией:** 2026-11-06: руководства тега Git v2.55.0, release notes 2.55.0; Conventional Commits 1.0.0

> **Выполнено:** 2026-11-06: Git 2.55.0, macOS, Bash 3.2.57; четыре учебных сценария и отдельные пробы карточек на синтетических данных

> **Границы запуска:** Временные репозитории и локальный bare remote; GitHub, серверные права и защита веток не проверялись

## `tools/git/history.md`

Исходная страница: [tools/git/history.md](../../tools/git/history.md).

> Сверено с документацией: 2026-11-06, Git v2.55.0 и release notes 2.55.0.

> Выполнено: 2026-11-06, Git 2.55.0, macOS, Bash 3.2.57; два сценария ниже.

## `tools/git/remotes.md`

Исходная страница: [tools/git/remotes.md](../../tools/git/remotes.md).

> Сверено с документацией: 2026-11-06, Git v2.55.0 и release notes 2.55.0.

> Выполнено: 2026-11-06, Git 2.55.0, macOS, Bash 3.2.57; сценарий с двумя копиями и локальным bare remote.

> Серверные права, GitHub и защита веток не проверялись.

> GitHub и серверные ограничения не проверяются этим сценарием.

## `tools/git/workflow.md`

Исходная страница: [tools/git/workflow.md](../../tools/git/workflow.md).

> Сверено с документацией: 2026-11-06, Git v2.55.0 и Conventional Commits 1.0.0.

> Выполнено: 2026-11-06, Git 2.55.0, macOS, Bash 3.2.57; сценарий ниже.

> Другие версии не запускались.

## `tools/github-pull-requests/README.md`

Исходная страница: [tools/github-pull-requests/README.md](../../tools/github-pull-requests/README.md).

> **Сверено с документацией:** 2026-11-06, GitHub Docs и руководство GitHub CLI

> **Выполнено:** Внешние действия GitHub и `gh` не выполнялись; локальные Git-сценарии проверены в теме Git

> Эти команды не выполнялись.

## `tools/github-pull-requests/merging.md`

Исходная страница: [tools/github-pull-requests/merging.md](../../tools/github-pull-requests/merging.md).

> Сверка: 2026-11-06.

> Справочный CLI-фрагмент, **внешнее изменение, не выполнялся**:

> Слияния и удаления веток на GitHub не выполнялись.

## `tools/github-pull-requests/review.md`

Исходная страница: [tools/github-pull-requests/review.md](../../tools/github-pull-requests/review.md).

> Сверка с документацией: 2026-11-06.

> Фрагменты **не выполнялись**.

> Создание PR, отправка ревью, изменение labels и запуск GitHub CI здесь не выполнялись.

## Проверка переноса

Дата: 2026-11-06.

- Сравнены 108 ограждённых блоков в 27 исходных страницах с `HEAD`: блоки совпадают побайтно.
- Проверены 384 относительные ссылки, включая ссылки на якоря: ошибок не найдено.
- Выполнен `git diff --check` для изменённых страниц и этого отчёта: ошибок не найдено.
- Примеры программ и команд повторно не выполнялись: перенос меняет только текст вне ограждённых блоков.
