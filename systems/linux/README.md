# Linux: терминал и повседневные задачи

Базовые операции с файлами, правами, процессами и сетью; отдельные рецепты для служб и пакетов.
Linux — ядро, а доступные команды определяются дистрибутивом, libc, shell и набором утилит.

| Параметр | Значение |
| --- | --- |
| Целевая среда | GNU/Linux; для shell-примеров явно выбран Bash |
| Предпосылки | Обычный пользователь, терминал; административные операции изучать на отдельной учебной системе |
| Сверено с документацией | 2026-11-06, GNU Bash/Coreutils/Findutils/Grep, Linux man-pages, systemd, Debian APT и DNF |
| Выполнено | 2026-11-06, только переносимые учебные скрипты Bash на macOS; Linux, GNU-specific flags, systemd, iproute2 и package managers не запускались |

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

## Быстрый поиск

Команды в таблице — отдельные операции для своей системы. Linux-only строки на текущем macOS-хосте не выполнялись.

| Задача | Команда | Подробнее |
| --- | --- | --- |
| Узнать каталог / окружение | `pwd`, `command -v bash`, `uname -s` | [Shell](shell-and-files.md) |
| Посмотреть файлы | `ls -la`, `find . -type f -name '*.log'` | [Файлы](shell-and-files.md) |
| Поиск по строкам | `grep -n 'ERROR' app.log` | [Поиск](shell-and-files.md#текст-потоки-и-коды-выхода) |
| Скопировать / сравнить | `cp source destination`, `cmp source destination` | [Учебный скрипт](shell-and-files.md#безопасный-практический-пример) |
| Проверить пользователя / права | `id`, `ls -ld path`, `umask` | [Права](permissions-and-processes.md) |
| Снимок процессов | `ps -ef`, `ps -p PID -o pid,ppid,stat,args` | [Процессы](permissions-and-processes.md#процессы-и-сигналы) |
| IP и маршруты, Linux | `ip -brief address`, `ip route` | [Сеть](network-and-services.md) |
| TCP listeners, Linux | `ss -lnt` | [Сеть](network-and-services.md) |
| systemd service, Linux | `systemctl status NAME.service` | [Службы](network-and-services.md#службы-systemd) |
| Логи systemd | `journalctl -u NAME.service -n 50 --no-pager` | [Службы](network-and-services.md#службы-systemd) |

## Базовый уровень

### Ориентироваться в shell

`pwd` показывает текущий каталог; `cd` меняет его в текущей shell. Относительные пути зависят от него.
`/` — корень файловой системы, `~` — домашний каталог пользователя, `.` / `..` — текущий/родительский.
Проверяй контекст перед операцией записи или удаления. Не используй имена файлов как команды.

Bash, Zsh и POSIX sh имеют различия. Здесь полный скрипт начинается с `#!/usr/bin/env bash`
и запускается `bash file.sh`; наличие `sh` не означает Bash. Команды PowerShell/cmd.exe отличаются.
[Пример](shell-and-files.md#безопасный-практический-пример) создаёт файлы исключительно в новом temp-каталоге.

## Средний уровень

### Соединять инструменты и проверять результат

`"$variable"` сохраняет пробелы и не даёт glob расширяться повторно. Одинарные кавычки сохраняют
буквальный текст; двойные допускают подстановки `$var` и `$(command)`.
Пайп передаёт stdout, а не произвольный «результат программы»; stderr перенаправляется отдельно.
Exit status важен: например, grep возвращает 1 при отсутствии совпадений, что не всегда является сбоем задачи.

[Права и процессы](permissions-and-processes.md) объясняют `rwx`, umask, PID, сигналы и ожидание дочернего процесса.
Не назначай `777`, не меняй владельца рекурсивно и не посылай сигнал всем совпавшим именам для «быстрого исправления».

## Продвинутый уровень

### Диагностировать систему по слоям

Сначала установи ОС и версии утилит, затем проверь процесс → listener → маршрут/DNS → HTTP.
При проблеме service различай stopped, failed, enabled и started: это разные состояния.
Пакетные менеджеры и init-системы зависят от дистрибутива; systemd отсутствует в части контейнеров и Linux-систем.
[Сеть и эксплуатация](network-and-services.md) отделяют чтение состояния от изменений.

macOS использует BSD-варианты многих инструментов и launchd, а не systemd.
GNU extensions `find -printf`, `stat -c`, `date -d`, `readlink -f` и различия `sed -i`
нельзя переносить между ОС без проверки. Выполнение переносимого скрипта на macOS
не считается выполнением Linux-рецепта.

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
