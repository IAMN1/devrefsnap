# Сеть, службы и пакеты Linux

Уровень: продвинутый. Предпосылки: Linux-система, понимание IP/HTTP и правил администрирования.
[К справочнику Linux](README.md).

Все команды этой страницы — справочные фрагменты. На macOS они **не выполнялись**;
активные изменения проверяй на отдельной учебной Linux-системе с разрешением владельца.

## Сеть: сначала чтение состояния

| Слой | Команда | Что видно |
| --- | --- | --- |
| Интерфейсы, iproute2 | `ip -brief address` | Адреса и состояние интерфейсов |
| Маршрут, iproute2 | `ip route` | Таблица маршрутов текущего network namespace |
| TCP listeners, iproute2 | `ss -lnt` | Прослушиваемые адреса/порты без DNS-подстановки |
| Процессы listeners | `ss -lntp` | PID/имена при достаточных правах |
| Resolver через NSS, glibc | `getent ahosts example.com` | Результат системного механизма разрешения имён |
| HTTP/TLS, curl | `curl --fail-with-body --connect-timeout 5 --max-time 10 https://example.com` | HTTP-ответ с ограничением времени; требует внешней сети |

`127.0.0.1:8000` слушает loopback, `0.0.0.0:8000` — все IPv4-интерфейсы namespace;
это само по себе не доказывает доступность через firewall/NAT/proxy.
`ping` проверяет ICMP и может блокироваться при рабочем HTTP. `dig` делает DNS-запросы,
но не полностью повторяет NSS/hosts resolution приложения. `getent` и iproute2 не гарантированы в minimal images.
`curl -k` отключает TLS-проверку и не исправляет сертификаты; диагностируй CA, имя сервера и время.

Для удалённого SSH: проверь адрес и ключ сервера при первом соединении, предпочитай настроенные ключи.
Фрагмент `ssh user@host` требует реальных значений; не отключай host key checking для устранения предупреждения.
Изменение адресов/маршрутов и firewall может оборвать доступ — такие команды здесь намеренно не предлагаются как быстрый рецепт.

## Службы systemd

Только для систем, где systemd действительно управляет службами.
`NAME.service` нужно заменить именем существующего unit. Чтение части логов может быть ограничено правами.

```text
systemctl status NAME.service
systemctl is-active NAME.service
systemctl is-enabled NAME.service
systemctl cat NAME.service
journalctl -u NAME.service -n 50 --no-pager
journalctl -u NAME.service --since '1 hour ago'
```

`is-active`/`is-enabled` возвращают код статуса; отсутствие active не всегда означает сбой команды диагностики.
`status` также может вернуть ненулевой код для inactive/failed. User services используют `systemctl --user`;
это другой manager/namespace, а не обход прав root.

| Изменение | Справочная команда | Последствие |
| --- | --- | --- |
| Запустить сейчас | `sudo systemctl start NAME.service` | Выполняет ExecStart и зависимости |
| Остановить | `sudo systemctl stop NAME.service` | Может прервать обслуживание запросов |
| Перезапустить | `sudo systemctl restart NAME.service` | Stop/start, возможен downtime |
| Включить для загрузки | `sudo systemctl enable NAME.service` | Создаёт связи автозапуска; без `--now` обычно не стартует сейчас |
| Перечитать изменённый unit | `sudo systemctl daemon-reload` | Перечитывает unit definitions; не равен reload приложения |

`reload` приложения поддерживается не каждым unit; изучи `systemctl cat`, ExecReload и документацию сервиса.
Не запускай restart только потому, что status красный: сначала сохрани логи и выясни причину.
В контейнере процесс может запускаться напрямую без systemd; на macOS используются другие инструменты.

## Пакеты: учитывать дистрибутив

Сначала прочитай `/etc/os-release` и проверь `command -v apt`, `command -v dnf` и версии.
Наличие одной команды не определяет всю систему. Таблица — справочник, **операции установки не выполнялись**.

| Задача | Debian/Ubuntu, APT | RPM-системы с DNF |
| --- | --- | --- |
| Поиск | `apt search PACKAGE` | `dnf search PACKAGE` |
| Информация | `apt show PACKAGE` | `dnf info PACKAGE` |
| Обновить metadata | `sudo apt update` | `sudo dnf makecache` |
| Установить пакет | `sudo apt install PACKAGE` | `sudo dnf install PACKAGE` |
| Удалить пакет | `sudo apt remove PACKAGE` | `sudo dnf remove PACKAGE` |

`PACKAGE` заменяется проверенным именем. Установка/удаление меняют общую систему и зависимости;
просматривай предлагаемый план транзакции. `apt update` обновляет metadata, а не все установленные пакеты.
Для автоматизации Debian используют документированные apt-get/apt-cache интерфейсы вместо интерактивного apt.
DNF4 и DNF5 отличаются отдельными командами/опциями; сверяй документацию установленной версии.
Arch, Alpine и другие системы имеют свои менеджеры и правила; команды APT/DNF не универсальны.

## Диск и ресурсы

`df -h` показывает файловые системы, `du -sh path` — оценку занятого места деревом пути.
Это разные величины: deleted-but-open files, sparse files и filesystem snapshots могут объяснять расхождения.
В Linux `free -h` и `/proc/meminfo` помогают смотреть память; «мало free» не равно «закончилась доступная память».
`/proc`, GNU df/du/free здесь не проверялись запуском; никакая очистка системных файлов не выполнялась.

## Источники и границы проверки

[Linux ip](https://man7.org/linux/man-pages/man8/ip.8.html), [ss](https://man7.org/linux/man-pages/man8/ss.8.html),
[curl](https://curl.se/docs/manpage.html),
[systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html),
[journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html),
[Debian APT](https://manpages.debian.org/bookworm/apt/apt.8.en.html),
[DNF](https://dnf.readthedocs.io/en/latest/command_ref.html).
Сверка: 2026-11-06. Linux runtime, службы, пакетные менеджеры, SSH и внешняя сеть не тестировались.
