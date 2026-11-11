import os
import socket
import subprocess


def scan(port):
    return subprocess.run(
        ["ss", "-H", "-lntp", f"sport = :{port}"],
        check=True, capture_output=True, text=True, timeout=5,
    ).stdout


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind(("127.0.0.1", 0))
    listener.listen(8)
    port = listener.getsockname()[1]
    pid = os.getpid()
    output = scan(port)
    assert f"127.0.0.1:{port}" in output
    assert f"pid={pid}," in output, "PID не виден: проверьте права и /proc"
    print(f"TCP port={port}; PID={pid}")
    print(output.strip())
    subprocess.run(
        ["ps", "-p", str(pid), "-o", "pid,user,comm,args"],
        check=True, timeout=5,
    )

assert not scan(port).strip(), "Порт уже появился в другом listener"
print("После закрытия: listener не найден")
