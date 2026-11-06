# Linux: терминал и повседневные задачи

Справочник содержит базовые операции с файлами, правами, процессами и сетью.
Отдельные рецепты описывают службы и пакеты.
Linux — ядро.
Доступные команды определяют дистрибутив, libc, shell и набор утилит.

## Быстрый поиск

Команды в таблице — отдельные операции для своей системы.
Поиск процесса по порту проверен в учебном Linux-контейнере; границы остальных проверок указаны ниже.

| Задача | Команда | Подробнее |
| --- | --- | --- |
| Узнать каталог / окружение | `pwd`, `command -v bash`, `uname -s` | [Shell](shell-and-files.md) |
| Посмотреть файлы | `ls -la`, `find . -type f -name '*.log'` | [Файлы](shell-and-files.md) |
| Поиск по строкам | `grep -n 'ERROR' app.log` | [Поиск](shell-and-files.md#текст-потоки-и-коды-выхода) |
| Скопировать / сравнить | `cp source destination`, `cmp source destination` | [Учебный скрипт](shell-and-files.md#безопасный-практический-пример) |
| Проверить пользователя / права | `id`, `ls -ld path`, `umask` | [Права](permissions-and-processes.md) |
| Снимок процессов | `ps -ef`, `ps -p PID -o pid,ppid,stat,args` | [Процессы](permissions-and-processes.md#процессы-и-сигналы) |
| IP и маршруты, Linux | `ip -brief address`, `ip route` | [Сеть](network-and-services.md) |
| Узнать, кто слушает TCP-порт 8000 | `ss -lntp 'sport = :8000'` | [Команда и PID](process-by-port.md#найти-tcp-listener) · [Права](process-by-port.md#если-pid-не-показан) · [Namespace](process-by-port.md#если-процесс-в-другом-namespace) |
| systemd service, Linux | `systemctl status NAME.service` | [Службы](network-and-services.md#службы-systemd) |
| Логи systemd | `journalctl -u NAME.service -n 50 --no-pager` | [Службы](network-and-services.md#службы-systemd) |

| Параметр | Значение |
| --- | --- |
| Целевая среда | GNU/Linux; для shell-примеров явно выбран Bash |
| Предпосылки | Обычный пользователь, терминал; административные операции изучайте на отдельной учебной системе |
| Сверено с документацией | 2026-11-06, GNU Bash/Coreutils/Findutils/Grep, Linux man-pages, systemd, Debian APT и DNF |
| Исходная проверка | 2026-11-06: переносимые учебные скрипты Bash на macOS |
| Поиск процесса по порту | 2026-11-06: [учебный пример, версии и границы](process-by-port.md); Debian 13.6, iproute2 6.15.0, procps-ng 4.0.4, util-linux 2.41.5, Python 3.13.5 |
| Остальные сценарии | GNU-specific flags, systemd и package managers как учебные рецепты не запускались |

## Навигация

- [Быстрый поиск](#быстрый-поиск)
- [Базовый уровень](#базовый-уровень)
- [Средний уровень](#средний-уровень)
- [Продвинутый уровень](#продвинутый-уровень)
- [Частые ошибки](#частые-ошибки)
- [Источники](#источники)
- [Shell, файлы и поиск](shell-and-files.md)
- [Права и процессы](permissions-and-processes.md)
- [Сеть, службы и пакеты](network-and-services.md)
- [Поиск процесса по порту](process-by-port.md)

## Базовый уровень

### Ориентироваться в shell

`pwd` показывает текущий каталог.
`cd` меняет текущий каталог в текущей shell.
Относительные пути зависят от текущего каталога.
`/` — корень файловой системы.
`~` — домашний каталог пользователя.
`.` и `..` обозначают текущий и родительский каталоги.
Проверьте контекст перед записью или удалением.
Не используйте имена файлов как команды.

Bash, Zsh и POSIX sh имеют различия.
Здесь полный скрипт начинается с `#!/usr/bin/env bash`.
Запускайте скрипт через `bash file.sh`.
Наличие `sh` не означает наличие Bash.
Команды PowerShell/cmd.exe отличаются.
[Пример](shell-and-files.md#безопасный-практический-пример) создаёт файлы исключительно в новом temp-каталоге.

## Средний уровень

### Соединять инструменты и проверять результат

`"$variable"` сохраняет пробелы и не даёт glob расширяться повторно.
Одинарные кавычки сохраняют буквальный текст.
Двойные кавычки допускают подстановки `$var` и `$(command)`.
Пайп передаёт stdout.
Перенаправляйте stderr отдельно.
Проверяйте код завершения команды.
Например, grep возвращает 1 при отсутствии совпадений.
Отсутствие совпадений не всегда означает сбой задачи.

[Права и процессы](permissions-and-processes.md) объясняют `rwx`, umask, PID, сигналы и ожидание дочернего процесса.
Не назначайте `777` для «быстрого исправления».
Не меняйте владельца рекурсивно для «быстрого исправления».
Не посылайте сигнал всем процессам с совпавшими именами для «быстрого исправления».

## Продвинутый уровень

### Диагностировать систему по слоям

Сначала определите ОС и версии утилит.
Затем проверьте процесс → listener → маршрут/DNS → HTTP.
При проблеме службы различайте состояния stopped, failed, enabled и started.
Пакетные менеджеры и init-системы зависят от дистрибутива.
В части контейнеров и Linux-систем systemd отсутствует.
[Сеть и эксплуатация](network-and-services.md) отделяют чтение состояния от изменений.

macOS использует BSD-варианты многих инструментов и launchd, а не systemd.
Проверяйте GNU extensions `find -printf`, `stat -c`, `date -d` и `readlink -f` перед переносом между ОС.
Отдельно учитывайте различия `sed -i`.
Выполнение переносимого скрипта на macOS не считается выполнением Linux-рецепта.

## Частые ошибки

| Симптом | Проверить |
| --- | --- |
| Файл с пробелом разделился на два аргумента | Кавычки вокруг пути/переменной |
| Permission denied после chmod | Право `x` каталогов пути, UID/GID, ACL, SELinux/AppArmor, mount flags |
| Команда работает в терминале, но не в cron/service | Shell, PATH, рабочий каталог, env и права |
| Порт открыт, HTTP не отвечает | Процесс, bind address, протокол, firewall, proxy и логи приложения |
| Service enabled, но не running | Enable задаёт старт по зависимостям/при загрузке, не обязательно запускает сейчас |
| `systemctl` не работает в контейнере | В нём может не быть systemd как service manager |

## Источники

- [GNU Bash](https://www.gnu.org/software/bash/manual/bash.html), [Coreutils](https://www.gnu.org/software/coreutils/manual/coreutils.html).
- [Findutils](https://www.gnu.org/software/findutils/manual/html_mono/find.html), [Grep](https://www.gnu.org/software/grep/manual/grep.html).
- [Linux ps](https://man7.org/linux/man-pages/man1/ps.1.html), [ip](https://man7.org/linux/man-pages/man8/ip.8.html), [ss](https://man7.org/linux/man-pages/man8/ss.8.html).
- [systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html), [journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html).

[Каталог систем](../README.md)
