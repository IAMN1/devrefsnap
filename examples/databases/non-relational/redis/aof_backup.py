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
