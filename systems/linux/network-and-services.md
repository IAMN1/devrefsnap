# Сеть, службы и пакеты Linux

Уровень: продвинутый. Предпосылки: Linux-система, понимание IP/HTTP и правил администрирования.
[К справочнику Linux](README.md).

Все команды этой страницы — справочные фрагменты.
На macOS команды **не выполнялись**.
Проверяйте активные изменения на отдельной учебной Linux-системе с разрешением владельца.

## Сеть: сначала чтение состояния

| Слой | Команда | Что видно |
| --- | --- | --- |
| Интерфейсы, iproute2 | `ip -brief address` | Адреса и состояние интерфейсов |
| Маршрут, iproute2 | `ip route` | Таблица маршрутов текущего network namespace |
| TCP listeners, iproute2 | `ss -lnt` | Прослушиваемые адреса/порты без DNS-подстановки |
| Процессы listeners | `ss -lntp` | PID/имена при достаточных правах |
| Resolver через NSS, glibc | `getent ahosts example.com` | Результат системного механизма разрешения имён |
| HTTP/TLS, curl | `curl --fail-with-body --connect-timeout 5 --max-time 10 https://example.com` | HTTP-ответ с ограничением времени; требует внешней сети |

`127.0.0.1:8000` слушает loopback.
`0.0.0.0:8000` слушает все IPv4-интерфейсы namespace.
Адрес прослушивания сам по себе не доказывает доступность через firewall/NAT/proxy.
`ping` проверяет ICMP и может блокироваться при рабочем HTTP.
`dig` выполняет DNS-запросы.
Результат `dig` не полностью повторяет разрешение имён приложения через NSS/hosts.
В минимальных образах `getent` и iproute2 могут отсутствовать.
`curl -k` отключает TLS-проверку и не исправляет сертификаты.
Проверьте CA, имя сервера и время.

При первом SSH-соединении проверьте адрес и ключ сервера.
Предпочитайте настроенные ключи.
Замените условные значения в `ssh user@host` реальными.
Не отключайте host key checking для устранения предупреждения.
Изменение адресов, маршрутов и firewall может оборвать доступ.
Такие команды здесь не приведены как быстрый рецепт.

## Службы systemd

Используйте команды только в системах, где systemd управляет службами.
Замените `NAME.service` именем существующего unit.
Права могут ограничивать чтение части логов.

```text
systemctl status NAME.service
systemctl is-active NAME.service
systemctl is-enabled NAME.service
systemctl cat NAME.service
journalctl -u NAME.service -n 50 --no-pager
journalctl -u NAME.service --since '1 hour ago'
```

`is-active`/`is-enabled` возвращают код статуса.
Отсутствие active не всегда означает сбой команды диагностики.
`status` также может вернуть ненулевой код для inactive/failed.
Пользовательские службы используют `systemctl --user`.
Этот вариант обращается к другому manager/namespace и не обходит права root.

| Изменение | Справочная команда | Последствие |
| --- | --- | --- |
| Запустить сейчас | `sudo systemctl start NAME.service` | Выполняет ExecStart и зависимости |
| Остановить | `sudo systemctl stop NAME.service` | Может прервать обслуживание запросов |
| Перезапустить | `sudo systemctl restart NAME.service` | Stop/start, возможен downtime |
| Включить для загрузки | `sudo systemctl enable NAME.service` | Создаёт связи автозапуска; без `--now` обычно не стартует сейчас |
| Перечитать изменённый unit | `sudo systemctl daemon-reload` | Перечитывает unit definitions; не равен reload приложения |

Не каждый unit поддерживает `reload` приложения.
Изучите `systemctl cat`, ExecReload и документацию службы.
Не запускайте restart только из-за красного status.
Сначала сохраните логи.
Выясните причину состояния.
В контейнере процесс может запускаться напрямую без systemd.
На macOS используются другие инструменты.

## Пакеты: учитывать дистрибутив

Сначала прочитайте `/etc/os-release`.
Проверьте `command -v apt` и `command -v dnf`.
Уточните версии найденных инструментов.
Наличие одной команды не определяет всю систему.
Таблица служит справочником.
**Операции установки не выполнялись**.

| Задача | Debian/Ubuntu, APT | RPM-системы с DNF |
| --- | --- | --- |
| Поиск | `apt search PACKAGE` | `dnf search PACKAGE` |
| Информация | `apt show PACKAGE` | `dnf info PACKAGE` |
| Обновить metadata | `sudo apt update` | `sudo dnf makecache` |
| Установить пакет | `sudo apt install PACKAGE` | `sudo dnf install PACKAGE` |
| Удалить пакет | `sudo apt remove PACKAGE` | `sudo dnf remove PACKAGE` |

Замените `PACKAGE` проверенным именем.
Установка и удаление меняют общую систему и зависимости.
Просмотрите предлагаемый план транзакции.
`apt update` обновляет metadata без обновления всех установленных пакетов.
Для автоматизации Debian используйте документированные интерфейсы apt-get/apt-cache вместо интерактивного apt.
DNF4 и DNF5 отличаются отдельными командами и опциями.
Сверяйте документацию установленной версии.
Arch, Alpine и другие системы имеют свои менеджеры и правила.
Команды APT/DNF не универсальны.

## Диск и ресурсы

`df -h` показывает файловые системы.
`du -sh path` оценивает место, занятое деревом указанного пути.
Это разные величины.
Расхождения могут объясняться deleted-but-open files, sparse files и filesystem snapshots.
В Linux `free -h` и `/proc/meminfo` помогают наблюдать память.
Малое значение free не означает отсутствие доступной памяти.
`/proc`, GNU df/du/free здесь не проверялись запуском.
Системные файлы не очищались.

## Источники и границы проверки

[Linux ip](https://man7.org/linux/man-pages/man8/ip.8.html), [ss](https://man7.org/linux/man-pages/man8/ss.8.html),
[curl](https://curl.se/docs/manpage.html),
[systemctl](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html),
[journalctl](https://www.freedesktop.org/software/systemd/man/latest/journalctl.html),
[Debian APT](https://manpages.debian.org/bookworm/apt/apt.8.en.html),
[DNF](https://dnf.readthedocs.io/en/latest/command_ref.html).
Сверка: 2026-11-06. Linux runtime, службы, пакетные менеджеры, SSH и внешняя сеть не тестировались.
