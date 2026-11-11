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
