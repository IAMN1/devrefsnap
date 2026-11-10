# Скопировать AOF Redis и проверить восстановление

Откройте страницу, чтобы восстановить данные Redis из полного набора файлов AOF.
AOF — журнал операций записи; Redis воспроизводит журнал при запуске.
TTL — оставшееся время жизни ключа.
Пример копирует файлы после штатной остановки учебного источника.
Источник будет недоступен во время копирования.

[Справочник Redis](README.md) · [Карточка AOF](operations.md#создать-и-восстановить-aof-копию) · [Пример RDB](backup-and-restore.md)

| Задача | Приём | Где |
| --- | --- | --- |
| Создать согласованную копию с остановкой источника | Скопировать весь appendonlydir | [Подготовка](#подготовить-запуск) · [Полная программа](#полный-пример) |
| Проверить состав журнала | Прочитать manifest, проверить BASE и INCR | [Состав файлов](#разобрать-состав-файлов) |
| Проверить значения и сроки | Сравнить данные, PEXPIRETIME и PTTL | [Результат](#проверить-результат) |

| Параметр | Значение |
| --- | --- |
| Уровень | Средний → продвинутый; административные команды выполняются только в учебных процессах |
| Предпосылки | Функции, словари, файлы, процессы, `with`, `try`/`finally` и `assert` в Python |
| Требования запуска | Redis Open Source 8.2.11, redis-cli 8.2.11, Python 3.14.7; Unix-сокеты на macOS или Linux |
| Зависимости | redis-server и redis-cli в PATH; Python использует только стандартную библиотеку |

## Разобрать состав файлов

Начиная с Redis 7.0 AOF может состоять из нескольких файлов.
Manifest — служебный список файлов и порядка их загрузки.
BASE содержит снимок исходных данных для переписанного журнала.
INCR содержит изменения после создания BASE; таких файлов может быть несколько.
Переписывание AOF создаёт более компактное представление текущих данных вместо полной истории команд.

Для этого примера возможен следующий состав каталога `appendonlydir`:

```text
appendonlydir/
├── appendonly.aof.manifest   # список частей журнала
├── appendonly.aof.2.base.rdb # BASE: начальное состояние в формате RDB
└── appendonly.aof.2.incr.aof # INCR: последующие команды записи
```

Номер `2` приведён как пример; программа читает имена из manifest.
Файл `.base.rdb` входит в AOF-набор, потому что включён `aof-use-rdb-preamble yes`.
Этот файл не заменяет весь журнал: для восстановления нужны также INCR и manifest.
Значение `appenddirname` задаёт имя каталога, а `appendfilename` — основу имён файлов.

Программа создаёт строку, hash и list, затем выполняет `BGREWRITEAOF` и ждёт завершения.
`BGREWRITEAOF` запускает фоновое переписывание; ответ команды ещё не означает готовность нового набора.
Проверки используют `INFO persistence`: rewrite завершён, не запланирован и имеет статус `ok`.
После переписывания программа меняет строку, дополняет list и создаёт два ключа с TTL.
Эти записи должны восстановиться из INCR, а исходные поля hash — из BASE.

Схема показывает этапы копирования и восстановления:

```mermaid
flowchart LR
    S[Учебный источник] -->|BGREWRITEAOF и последующие записи| J[BASE + INCR + manifest]
    J -->|штатно остановить источник| F[Неизменяемый набор файлов]
    F -->|скопировать весь каталог| B[Резервная копия]
    B -->|поместить в новый каталог до запуска| T[Другой Redis с appendonly yes]
    T -->|прочитать данные и сроки| V[Проверки]
```

`SHUTDOWN NOSAVE` не создаёт отдельный RDB-снимок, но при штатной остановке Redis сбрасывает AOF на диск.
Программа требует успешного завершения источника перед копированием.
В примере `appendfsync always` выполняет синхронизацию AOF при записи; настройка выбрана для небольшого учебного набора.
Она не является универсальной рекомендацией для рабочего сервера.
Автоматическое переписывание отключено; единственное ручное переписывание завершается до остановки.

## Подготовить запуск

Установите Redis Open Source 8.2.11 по [официальным инструкциям](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/).
Добавьте `redis-server` и `redis-cli` этой версии в PATH.
Создайте отдельную учебную папку.
Сохраните [полный блок ниже](#полный-пример) как `aof_backup.py` в этой папке.
Выполните команды оболочки:

```bash
redis-server --version
redis-cli --version
python3 aof_backup.py
```

Дополнительные пакеты Python и другие файлы репозитория не нужны.
Программа сама создаёт процессы и не принимает адрес существующего Redis.
Unix-сокет — локальный файл для соединения; TCP отключён.
Все данные находятся в новом закрытом каталоге `/tmp/redis-aof-*`.

Запускайте программу без `-O`: она проверяет результаты через `assert`.
Программа отклоняет запуск с отключёнными проверками до создания каталога и процессов.

## Полный пример

Полный `aof_backup.py` проверяет исходный набор, обе копии и восстановленные данные.
SHA-256 — контрольная сумма содержимого; она позволяет сравнить байты файлов до запуска целевого Redis.
После запуска Redis может дописывать журнал, поэтому побайтовое сравнение выполняется заранее.

`inventory()` проверяет только контролируемый набор этого примера, а не произвольный manifest Redis.
Для этого набора ожидаются одна BASE в формате RDB, хотя бы одна непустая INCR и manifest.
Не переносите эти условия без изменения на произвольный AOF-каталог.
`INFO` возвращается как текст даже с `redis-cli --json`; помощник обрабатывает такой ответ отдельно.

<!-- example: redis/aof_backup.py -->
```python
import hashlib
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import time


MANIFEST = "appendonly.aof.manifest"


def command(socket, *args):
    result = subprocess.run(
        ["redis-cli", "-e", "--json", "-s", str(socket), *map(str, args)],
        check=True, capture_output=True, text=True, timeout=5,
    )
    # INFO выводится как текст даже с флагом --json.
    return result.stdout if args[0] == "INFO" else json.loads(result.stdout)


def wait_until(predicate, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.05)
    raise TimeoutError("Учебная операция не завершилась вовремя")


def persistence(socket):
    lines = command(socket, "INFO", "persistence").splitlines()
    return dict(line.split(":", 1) for line in lines if ":" in line)


def rewrite_finished(socket):
    info = persistence(socket)
    return info["aof_rewrite_in_progress"] == "0" and info["aof_rewrite_scheduled"] == "0"


def start_server(root, name, managed):
    directory = root / name
    directory.mkdir(exist_ok=True)
    socket = root / f"{name}.sock"
    log = root / f"{name}.log"
    with log.open("w") as output:
        process = subprocess.Popen([
            "redis-server", "--port", "0", "--unixsocket", str(socket),
            "--unixsocketperm", "700", "--dir", str(directory),
            "--save", "", "--appendonly", "yes", "--appendfsync", "always",
            "--appenddirname", "appendonlydir", "--appendfilename", "appendonly.aof",
            "--auto-aof-rewrite-percentage", "0", "--aof-use-rdb-preamble", "yes",
            "--aof-load-truncated", "no", "--daemonize", "no", "--loglevel", "warning",
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
            assert process.returncode == 0
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


def inventory(directory):
    # Это проверка своего учебного набора, а не универсальный парсер manifest.
    entries = []
    for line in (directory / MANIFEST).read_text().splitlines():
        fields = shlex.split(line)
        assert len(fields) >= 6 and len(fields) % 2 == 0
        entry = dict(zip(fields[::2], fields[1::2]))
        name = entry["file"]
        assert Path(name).name == name and name not in (".", "..")
        assert entry["type"] in ("b", "i") and int(entry["seq"]) > 0
        entries.append(entry)
    bases = [entry for entry in entries if entry["type"] == "b"]
    increments = [entry for entry in entries if entry["type"] == "i"]
    assert len(bases) == 1 and increments
    names = [entry["file"] for entry in entries]
    assert len(names) == len(set(names))
    expected = set(names) | {MANIFEST}
    actual = {file.name for file in directory.iterdir()}
    if actual != expected:
        raise ValueError(f"Неверный набор AOF: ожидается {sorted(expected)}, найдено {sorted(actual)}")
    assert bases[0]["file"].endswith(".base.rdb")
    assert (directory / bases[0]["file"]).read_bytes().startswith(b"REDIS")
    for entry in entries:
        file = directory / entry["file"]
        assert file.is_file() and file.stat().st_size > 0
    return entries


def checksums(directory):
    return {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
            for file in directory.iterdir()}


def main():
    if not __debug__:
        raise RuntimeError("Запустите без -O: проверки assert обязательны")
    for executable in ("redis-server", "redis-cli"):
        if shutil.which(executable) is None:
            raise RuntimeError(f"Добавьте {executable} в PATH")
    root = Path(tempfile.mkdtemp(prefix="redis-aof-", dir="/tmp"))
    print(f"Учебная папка: {root}", flush=True)
    managed = []
    try:
        source_process, source = start_server(root, "source", managed)
        assert command(source, "DBSIZE") == 0
        assert command(source, "SET", "demo:title", "before rewrite") == "OK"
        assert command(source, "HSET", "demo:profile", "id", "42", "name", "Alice") == 2
        assert command(source, "RPUSH", "demo:queue", "first", "second") == 2
        wait_until(lambda: rewrite_finished(source))
        assert command(source, "BGREWRITEAOF") == "Background append only file rewriting started"
        wait_until(lambda: rewrite_finished(source))
        assert persistence(source)["aof_last_bgrewrite_status"] == "ok"

        # Эти изменения идут в INCR после создания базового снимка.
        assert command(source, "SET", "demo:title", "after rewrite") == "OK"
        assert command(source, "RPUSH", "demo:queue", "third") == 3
        assert command(source, "SET", "demo:live", "still valid", "PX", 120000) == "OK"
        assert command(source, "SET", "demo:expired", "short lived", "PX", 5000) == "OK"
        live_deadline = command(source, "PEXPIRETIME", "demo:live")
        short_deadline = command(source, "PEXPIRETIME", "demo:expired")
        ttl_before = command(source, "PTTL", "demo:live")
        assert persistence(source)["aof_last_write_status"] == "ok"

        # NOSAVE запрещает отдельный RDB, но не отменяет сброс AOF при штатной остановке.
        stop_server(source_process, source)
        assert source_process.returncode == 0
        assert time.time_ns() // 1_000_000 < short_deadline
        journal = root / "source" / "appendonlydir"
        entries = inventory(journal)
        assert not (root / "source" / "dump.rdb").exists()
        backup = root / "backup" / "appendonlydir"
        shutil.copytree(journal, backup)
        assert inventory(backup) == entries
        before = checksums(journal)
        assert checksums(backup) == before
        for entry in entries:
            print(f"{entry['type']}: {entry['file']}")
        print(f"manifest: {MANIFEST}")

        # Короткий ключ истекает, пока источник уже остановлен.
        wait_until(lambda: time.time_ns() // 1_000_000 > short_deadline, timeout=10)
        restore = root / "restored"
        restore.mkdir()
        shutil.copytree(backup, restore / "appendonlydir")
        assert inventory(restore / "appendonlydir") == entries
        assert checksums(restore / "appendonlydir") == before
        _, target = start_server(root, "restored", managed)

        assert command(target, "GET", "demo:title") == "after rewrite"
        assert command(target, "HGETALL", "demo:profile") == {"id": "42", "name": "Alice"}
        assert command(target, "LRANGE", "demo:queue", 0, -1) == ["first", "second", "third"]
        for key in ("demo:title", "demo:profile", "demo:queue"):
            assert command(target, "PTTL", key) == -1
        assert command(target, "GET", "demo:live") == "still valid"
        assert command(target, "PEXPIRETIME", "demo:live") == live_deadline
        ttl_after = command(target, "PTTL", "demo:live")
        assert 0 < ttl_after < ttl_before <= 120000
        assert command(target, "EXISTS", "demo:expired") == 0
        assert command(target, "PTTL", "demo:expired") == -2
        assert command(target, "DBSIZE") == 4
        assert persistence(target)["aof_enabled"] == "1"
        print("OK: BASE + INCR восстановили строку, hash и порядок list")
        print("OK: абсолютный срок сохранён, оставшийся TTL уменьшился")
        print("OK: постоянные ключи без TTL, просроченный ключ отсутствует")
        print("OK: manifest и все его файлы скопированы без изменения байтов")
        print(f"PTTL до/после: {ttl_before}/{ttl_after} мс")
    finally:
        for process, socket in reversed(managed):
            stop_server(process, socket)


if __name__ == "__main__":
    main()
```

## Проверить результат

Ожидается код завершения `0` и такие сообщения:

```text
OK: BASE + INCR восстановили строку, hash и порядок list
OK: абсолютный срок сохранён, оставшийся TTL уменьшился
OK: постоянные ключи без TTL, просроченный ключ отсутствует
OK: manifest и все его файлы скопированы без изменения байтов
```

Программа также выводит учебный каталог, имена частей и значения PTTL до и после восстановления.
Имена файлов и числа PTTL зависят от запуска.
`PEXPIRETIME` — абсолютный момент истечения в миллисекундах Unix-времени.
`PTTL` — оставшееся время в миллисекундах; `-1` означает отсутствие срока, `-2` — отсутствие ключа.

| Объект | Ожидаемый результат |
| --- | --- |
| Manifest и перечисленные части | Все файлы присутствуют; SHA-256 совпадает у источника и двух копий |
| `demo:title` | `after rewrite`, то есть изменение из INCR применилось |
| `demo:profile` | Поля `id=42` и `name=Alice` из BASE сохранились |
| `demo:queue` | `first`, `second`, `third`: сохранены исходный порядок и добавление из INCR |
| Три постоянных ключа | `PTTL == -1` |
| `demo:live` | Значение сохранено; PEXPIRETIME прежний, оставшийся PTTL положителен и уменьшился |
| `demo:expired` | Истёк во время простоя; отсутствует, `PTTL == -2` |
| БД 0 | Четыре ключа; AOF включён |

Время жизни продолжает уменьшаться во время остановки.
Восстановление AOF не выдаёт ключу исходные 120 секунд заново.
Блок `finally` останавливает только созданные процессы и при ошибке проверки.
Учебный каталог с источником, копией и журналами остаётся для просмотра.
После изучения удалите только каталог, который вывела программа.

## Ограничения

Сценарий рассчитан на копирование остановленного источника, одинаковые бинарные файлы Redis и стабильные часы одного компьютера.
Он не показывает копирование работающего экземпляра или переключение действующего RDB-сервера на AOF.
Для копирования без остановки нужен отдельный порядок управления переписыванием и границей копии.

Пример размещает файлы только в новом каталоге до запуска целевого Redis.
Не заменяйте AOF работающего экземпляра этим рецептом.
Пустой каталог при запуске с `appendonly yes` может создать новую пустую БД; это не подтверждает восстановление.
Поэтому программа проверяет наличие всего набора до запуска и состав данных после запуска.

`aof-load-truncated no` запрещает автоматическое принятие оборванного хвоста журнала.
Программа не ремонтирует файлы и не запускает `redis-check-aof --fix`.
Такой ремонт может удалить часть истории; сначала нужны сохранённая копия и оценка последствий.

Пример использует БД 0 и маленькие синтетические данные.
Он не проверяет конкурирующие записи, сбой питания, нехватку диска, модули, Cluster или разные версии Redis.
Большая задержка запуска или скачок часов может нарушить временные условия; проверки остановят сценарий.
Копия на том же компьютере не защищает от потери этого компьютера.
Для рабочего резервного копирования нужны отдельное хранение и регулярные проверки восстановления.

## Источники

- [Redis persistence: состав AOF и резервное копирование](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/).
- [BGREWRITEAOF](https://redis.io/docs/latest/commands/bgrewriteaof/), [SHUTDOWN](https://redis.io/docs/latest/commands/shutdown/), [INFO](https://redis.io/docs/latest/commands/info/).
- [EXPIRE: сроки и сохранение](https://redis.io/docs/latest/commands/expire/), [PEXPIRETIME](https://redis.io/docs/latest/commands/pexpiretime/).
- [Redis 8.2.11: формат manifest и загрузка AOF](https://github.com/redis/redis/blob/8.2.11/src/aof.c), [остановка сервера](https://github.com/redis/redis/blob/8.2.11/src/server.c).
- [Redis 8.2.11: release notes](https://github.com/redis/redis/releases/tag/8.2.11).

[Карточка AOF](operations.md#создать-и-восстановить-aof-копию) · [Пример RDB](backup-and-restore.md) · [Справочник Redis](README.md) · [Указатель задач](../../../tasks/README.md#redis)
