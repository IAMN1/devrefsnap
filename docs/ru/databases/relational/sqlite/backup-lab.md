
# Проверить копию SQLite в учебном окружении

[English](../../../../en/databases/relational/sqlite/backup-lab.md)

Повторите backup/restore без изменения рабочей БД.
Выберите Python API или CLI.
Каждый сценарий создаёт и удаляет только свой временный каталог с синтетическими данными.
[Карточки backup/restore](backup-and-restore.md) · [Миграция схемы](backup-and-migrations.md).

| Задача | Сценарий | Проверки |
| --- | --- | --- |
| Проверить копию открытой WAL-БД | [Python API](#проверить-backup-api) | Снимок, схема, ограничения, триггер и отказы |
| Проверить бинарную и SQL-копию | [CLI](#проверить-cli-копию-и-sql-dump) | `.backup`, `.restore`, `.dump`, integrity/FK и поведение |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; ограничения WAL и отказы — продвинутый |
| Предпосылки | Python 3.14 со sqlite3 либо Bash и sqlite3 CLI; схема STRICT требует SQLite 3.37 |


## Проверить backup API

Сохраните полный пример как `backup.py`.
Запустите `python3.14 backup.py`.
Зависимости входят в стандартную библиотеку Python.

Источник остаётся открытым в WAL; конкурирующего writer здесь нет.
После создания копии сценарий меняет источник.
Восстановленная БД должна содержать прежний снимок.
Целевые файлы резервируются через `touch(exist_ok=False)` и не заменяют существующие файлы.
При ошибке backup созданная цель может остаться неполной; сценарий удалит её вместе со своим каталогом.

[`sqlite/backup.py`](../../../../../examples/databases/relational/sqlite/backup.py)

**Результат:** `Python backup/restore OK; SQLite ...`.
Копия сохраняет исходную `alice`; источник после копии содержит `alice-live`.
Проверка триггера откатывает свои изменения в восстановленной БД.
Занятое имя, отсутствующий источник и неверный формат файла вызывают ожидаемые отказы.
Это не сценарий восстановления уже повреждённой БД через recovery-инструменты.


## Проверить CLI-копию и SQL dump

Сохраните полный пример как `backup-cli.sh`.
Запустите `bash backup-cli.sh`.
Зависимости: Bash и sqlite3 CLI с поддержкой STRICT.
Скрипт сам создаёт исходную БД; внешние файлы и сервер не нужны.

`set -C` защищает новые целевые имена от перезаписи перенаправлением.
Команды `.backup` и `.restore` сами по себе могут заменить содержимое существующей цели.
Все пути ниже относятся только к созданному временному каталогу.

[`sqlite/backup-cli.sh`](../../../../../examples/databases/relational/sqlite/backup-cli.sh)

**Результат:** `CLI backup/restore OK`.
Обе восстановленные БД содержат ожидаемые строки, индекс и работающий триггер.
Проверки подтверждают отказ FK/CHECK и сохранность исходного файла.
Отдельная учебная БД показывает нарушение FK при успешном `integrity_check`.
Версия CLI проверяется отдельно: `sqlite3 --version`.


## Источники

- [Backup API](https://www.sqlite.org/backup.html), [Python Connection.backup](https://docs.python.org/3.14/library/sqlite3.html#sqlite3.Connection.backup), [CLI и dump](https://www.sqlite.org/cli.html).
- [Integrity check](https://www.sqlite.org/pragma.html#pragma_integrity_check), [foreign key check](https://www.sqlite.org/pragma.html#pragma_foreign_key_check), [WAL](https://www.sqlite.org/wal.html).
- [Release notes 3.53.4](https://www.sqlite.org/releaselog/3_53_4.html), [release notes 3.54.0](https://www.sqlite.org/releaselog/3_54_0.html).
