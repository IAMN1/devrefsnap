#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY_CHILD'
import selectors
import signal
import subprocess
import sys

child_code = """
import signal
signal.signal(signal.SIGTERM, signal.SIG_DFL)
print("ready", flush=True)
signal.pause()
"""
child = subprocess.Popen(
    [sys.executable, "-c", child_code], stdout=subprocess.PIPE, text=True
)
try:
    with selectors.DefaultSelector() as selector:
        selector.register(child.stdout, selectors.EVENT_READ)
        if not selector.select(timeout=5):
            raise TimeoutError("child did not report readiness")
    if child.stdout.readline() != "ready\n":
        raise RuntimeError("child exited before readiness")
    child.terminate()
    status = child.wait(timeout=5)
    if status != -signal.SIGTERM:
        raise AssertionError(f"expected SIGTERM, got {status}")
finally:
    if child.poll() is None:
        child.kill()
        child.wait(timeout=5)
    child.stdout.close()
print("process OK")
PY_CHILD
