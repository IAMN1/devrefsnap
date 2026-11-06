# Создать RDB-копию Redis и проверить восстановление

Откройте страницу, чтобы сохранить данные Redis и проверить копию на отдельном экземпляре.
RDB — файл снимка данных на определённый момент.
TTL — оставшееся время жизни ключа; после истечения ключ становится недоступен.
Пример проверяет значения и сроки, а не только наличие файла.

[Справочник Redis](README.md) · [Короткая карточка](operations.md#создать-и-восстановить-rdb-копию)

| Задача | Приём | Где |
| --- | --- | --- |
| Создать копию и восстановить данные | Два отдельных Redis и один файл Python | [Подготовка](#подготовить-запуск) · [Полная программа](#полный-пример) |
| Проверить сроки жизни | Сравнить срок истечения и оставшийся TTL | [Ожидаемый результат](#проверить-результат) |
| Понять границы восстановления | Учесть момент снимка, AOF и часы | [Ограничения](#ограничения) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний; административные команды выполняются только в учебных процессах |
| Предпосылки | Функции, словари, `with`, `try`/`finally`, `assert`, процессы и файлы Python |
| Среда | Redis Open Source 8.2.11, redis-cli 8.2.11, Python 3.14.7; macOS или Linux с Unix-сокетами |
| Зависимости | Два бинарных файла Redis в PATH; Python использует только стандартную библиотеку |

## Как устроен пример

Программа сама создаёт два процесса Redis с разными Unix-сокетами.
Unix-сокет — локальный файл для соединения с процессом без TCP-порта.
Каталог каждого запуска создаётся заново в `/tmp` и доступен только текущему пользователю.
Программа не принимает адрес существующего Redis.

Источник содержит строку, hash с полями профиля и list с двумя элементами.
Ещё два строковых ключа имеют TTL: 120 секунд и 5 секунд.
Пример выполняет следующие этапы:

```mermaid
flowchart LR
    S[Учебный источник] -->|BGSAVE: завершить снимок| D[dump.rdb]
    D -->|скопировать готовый файл| B[backup.rdb]
    B -->|поместить до запуска| R[Новый каталог dump.rdb]
    R -->|запустить другой Redis| T[Проверить значения и сроки]
```

`BGSAVE` начинает фоновое сохранение; ответ команды ещё не означает готовность файла.
Программа ждёт завершения по `INFO persistence` и проверяет статус `ok`.
В свежем каталоге нет старого `dump.rdb`, который можно случайно принять за новую копию.
После завершения программа копирует файл в `backup.rdb` и сравнивает SHA-256.
SHA-256 — контрольная сумма содержимого; равенство сумм подтверждает совпадение скопированных байтов.
Пригодность копии подтверждается последующим запуском Redis и проверкой данных.

После копирования программа изменяет строку и добавляет ключ в источнике.
Затем программа останавливает источник через `SHUTDOWN NOSAVE` и ждёт истечения короткого TTL.
Эта команда завершает только созданный учебный процесс, без сохранения поздних изменений.
Копия загружается в другой процесс из нового каталога с отключённым AOF.
AOF — журнал операций записи; при одновременном включении AOF и RDB Redis предпочитает AOF при запуске.

## Подготовить запуск

Установите Redis Open Source 8.2.11 по [официальным инструкциям](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/).
Добавьте `redis-server` и `redis-cli` этой версии в PATH.
Создайте отдельную учебную папку.
Сохраните [программу ниже](#полный-пример) как `rdb_backup.py` в этой папке.
Выполните команды оболочки из учебной папки:

```bash
redis-server --version
redis-cli --version
python3 rdb_backup.py
```

Используйте Python 3.14.7 для воспроизведения.
Дополнительные пакеты Python не нужны.
Запускайте программу без `-O`: проверки `assert` обязательны.
Программа отклоняет запуск с отключёнными проверками до создания процессов.

## Полный пример

Полный файл `rdb_backup.py` создаёт данные, копирует RDB и выполняет проверки.
Он запускает `redis-cli` с `--json` для разбора ответов.
Команда `INFO` возвращается как текст даже при этом флаге; помощник обрабатывает её отдельно.
Флаг `-e` превращает ошибку команды Redis в ненулевой код завершения клиента.
Все Redis-команды передаются отдельными аргументами, без выполнения команд оболочкой.

<!-- example: redis/rdb_backup.py -->
```python
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


def command(socket, *args):
    result = subprocess.run(
        ["redis-cli", "-e", "--json", "-s", str(socket), *map(str, args)],
        check=True, capture_output=True, text=True, timeout=5,
    )
    # redis-cli выводит INFO как текст даже с флагом --json.
    if args[0] == "INFO":
        return result.stdout
    return json.loads(result.stdout)


def wait_until(predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise TimeoutError("Учебная операция не завершилась за отведённое время")


def persistence(socket):
    lines = command(socket, "INFO", "persistence").splitlines()
    return dict(line.split(":", 1) for line in lines if ":" in line)


def start_server(root, name, managed):
    directory = root / name
    directory.mkdir(exist_ok=True)
    socket = root / f"{name}.sock"
    log = root / f"{name}.log"
    with log.open("w") as output:
        process = subprocess.Popen([
            "redis-server", "--port", "0", "--unixsocket", str(socket),
            "--unixsocketperm", "700", "--dir", str(directory),
            "--dbfilename", "dump.rdb", "--save", "", "--appendonly", "no",
            "--daemonize", "no", "--loglevel", "warning",
        ], stdout=output, stderr=subprocess.STDOUT)
    managed.append((process, socket))

    def ready():
        if process.poll() is not None:
            raise RuntimeError(f"Redis не запустился; журнал: {log}\n{log.read_text()}")
        try:
            return command(socket, "PING") == "PONG"
        except subprocess.CalledProcessError:
            return False

    wait_until(ready)
    return process, socket


def stop_server(process, socket):
    if process.poll() is None:
        try:
            subprocess.run(
                ["redis-cli", "-e", "-s", str(socket), "SHUTDOWN", "NOSAVE"],
                check=True, capture_output=True, text=True, timeout=5,
            )
            process.wait(timeout=5)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


def main():
    if not __debug__:
        raise RuntimeError("Запустите пример без -O: проверки assert обязательны")
    for executable in ("redis-server", "redis-cli"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Добавьте {executable} в PATH")
    root = Path(tempfile.mkdtemp(prefix="redis-rdb-", dir="/tmp"))
    print(f"Учебная папка: {root}", flush=True)
    managed = []
    try:
        source_process, source = start_server(root, "source", managed)
        assert command(source, "DBSIZE") == 0
        assert command(source, "SET", "demo:title", "before snapshot") == "OK"
        assert command(source, "HSET", "demo:profile", "id", "42", "name", "Alice") == 2
        assert command(source, "RPUSH", "demo:queue", "first", "second") == 2
        assert command(source, "SET", "demo:live", "still valid", "PX", 120000) == "OK"
        assert command(source, "SET", "demo:expired", "short lived", "PX", 5000) == "OK"
        live_deadline = command(source, "PEXPIRETIME", "demo:live")
        short_deadline = command(source, "PEXPIRETIME", "demo:expired")
        ttl_before = command(source, "PTTL", "demo:live")

        # В свежем каталоге нет старого RDB; ждём завершения именно этой копии.
        assert command(source, "BGSAVE") == "Background saving started"
        wait_until(lambda: persistence(source)["rdb_bgsave_in_progress"] == "0")
        assert persistence(source)["rdb_last_bgsave_status"] == "ok"
        dump = root / "source" / "dump.rdb"
        assert dump.is_file() and dump.stat().st_size > 0
        assert command(source, "GET", "demo:expired") == "short lived"
        assert command(source, "PTTL", "demo:expired") > 0

        backup = root / "backup.rdb"
        with dump.open("rb") as original, backup.open("xb") as copy:
            shutil.copyfileobj(original, copy)
        checksum = hashlib.sha256(backup.read_bytes()).hexdigest()
        assert checksum == hashlib.sha256(dump.read_bytes()).hexdigest()

        # Эти записи сделаны после снимка и не должны попасть в восстановление.
        assert command(source, "SET", "demo:title", "after snapshot") == "OK"
        assert command(source, "SET", "demo:later", "not backed up") == "OK"
        stop_server(source_process, source)
        wait_until(lambda: time.time_ns() // 1_000_000 > short_deadline, timeout=10)

        # Создаём новый каталог; существующие данные не перезаписываем.
        restore = root / "restored"
        restore.mkdir()
        with backup.open("rb") as original, (restore / "dump.rdb").open("xb") as copy:
            shutil.copyfileobj(original, copy)
        assert hashlib.sha256((restore / "dump.rdb").read_bytes()).hexdigest() == checksum
        _, target = start_server(root, "restored", managed)

        assert command(target, "GET", "demo:title") == "before snapshot"
        assert command(target, "HGETALL", "demo:profile") == {"id": "42", "name": "Alice"}
        assert command(target, "LRANGE", "demo:queue", 0, -1) == ["first", "second"]
        for key in ("demo:title", "demo:profile", "demo:queue"):
            assert command(target, "PTTL", key) == -1
        assert command(target, "GET", "demo:live") == "still valid"
        assert command(target, "PEXPIRETIME", "demo:live") == live_deadline
        ttl_after = command(target, "PTTL", "demo:live")
        assert 0 < ttl_after < ttl_before <= 120000
        assert command(target, "EXISTS", "demo:expired", "demo:later") == 0
        assert command(target, "PTTL", "demo:expired") == -2
        assert command(target, "DBSIZE") == 4
        print("OK: string, hash, list и ключи без срока восстановлены")
        print("OK: срок истечения сохранён, оставшийся TTL уменьшился")
        print("OK: просроченный ключ и запись после снимка отсутствуют")
        print(f"PTTL до/после: {ttl_before}/{ttl_after} мс")
        print(f"RDB SHA-256: {checksum}")
    finally:
        for process, socket in reversed(managed):
            stop_server(process, socket)


if __name__ == "__main__":
    main()
```

## Проверить результат

Ожидается завершение с кодом `0` и такими строками:

```text
OK: string, hash, list и ключи без срока восстановлены
OK: срок истечения сохранён, оставшийся TTL уменьшился
OK: просроченный ключ и запись после снимка отсутствуют
```

Программа также выводит учебный каталог, два значения PTTL и контрольную сумму RDB.
Числа PTTL и контрольная сумма зависят от момента запуска.
`PTTL` возвращает оставшееся время в миллисекундах.
Значение `-1` означает ключ без срока; значение `-2` означает отсутствие ключа.
`PEXPIRETIME` возвращает абсолютный момент истечения в миллисекундах Unix-времени.

| Проверяемый объект | Ожидаемый результат |
| --- | --- |
| `demo:title` | `before snapshot`; изменение после снимка не возвращается |
| `demo:profile` | Поля `id=42` и `name=Alice` сохранены |
| `demo:queue` | Элементы `first`, `second` сохранили порядок |
| Три ключа без TTL | `PTTL == -1` |
| `demo:live` | Значение сохранено; PEXPIRETIME совпадает, оставшийся PTTL положителен и меньше прежнего |
| `demo:expired` | Ключ отсутствует; `PTTL == -2` |
| `demo:later` | Ключ, созданный после снимка, отсутствует |
| Размер восстановленной БД 0 | Четыре ключа |

- [ ] Проверьте содержимое строки, hash и list.
- [ ] Проверьте отсутствие TTL у постоянных ключей.
- [ ] Проверьте неизменность абсолютного момента истечения временного ключа.
- [ ] Проверьте уменьшение оставшегося TTL.
- [ ] Проверьте отсутствие просроченного ключа.
- [ ] Проверьте отсутствие записи после снимка.

Redis хранит момент истечения, поэтому TTL продолжает уменьшаться во время простоя.
Восстановление не выдаёт ключу исходные 120 секунд заново.

Блок `finally` останавливает созданные процессы и при ошибке проверки.
Учебный каталог с копией, исходным RDB и журналами остаётся для просмотра.
После изучения удалите только каталог, который вывела программа.

## Ограничения

Этот пример использует маленький набор данных и один компьютер со стабильными часами.
Большое расхождение часов между компьютерами меняет результат проверки сроков.
Если машина работает слишком медленно, короткий ключ может истечь до сохранения; соответствующая проверка остановит сценарий.

RDB относится к моменту снимка, а не к моменту восстановления.
Изменения после снимка в эту копию не входят.
Файл RDB может содержать несколько логических БД; пример создаёт данные только в БД 0.

Не подменяйте файл работающего экземпляра этим рецептом.
Пример размещает RDB только в новом каталоге до запуска целевого Redis.
Для восстановления нужны совместимые формат RDB, версия Redis и используемые модули.
Пример использует одинаковые бинарные файлы для обоих процессов.

Сценарий не проверяет конкурентные записи во время BGSAVE, повреждённые копии, AOF, Cluster или восстановление после сбоя питания.
Копия на том же компьютере демонстрирует механизм и не защищает от потери этого компьютера.
Для рабочей резервной копии нужны отдельное хранение и регулярные проверки восстановления.

## Источники

- [Redis: RDB, копирование готового файла и восстановление](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/).
- [BGSAVE](https://redis.io/docs/latest/commands/bgsave/), [INFO persistence](https://redis.io/docs/latest/commands/info/).
- [EXPIRE: сроки и сохранение](https://redis.io/docs/latest/commands/expire/), [PTTL](https://redis.io/docs/latest/commands/pttl/), [PEXPIRETIME](https://redis.io/docs/latest/commands/pexpiretime/).
- [Redis 8.2.11: сохранение и загрузка RDB](https://github.com/redis/redis/blob/8.2.11/src/rdb.c).
- [Redis 8.2.11: release notes](https://github.com/redis/redis/releases/tag/8.2.11).

[Карточка RDB](operations.md#создать-и-восстановить-rdb-копию) · [Справочник Redis](README.md) · [Указатель задач](../../../tasks/README.md#redis)
