#!/usr/bin/env python3
"""Выделите добавленные строки для ручного ревью. Сигналы не блокируют PR."""
import argparse
from collections import Counter
import json
import re
import subprocess
import sys

PATTERNS = {
    "external-url": r"(?:https?|ftp|ssh)://|\bwww\.",
    "dependency": r"\b(?:pip3?\s+install|uv\s+(?:add|pip)|npm\s+(?:install|ci)|go\s+get|apt(?:-get)?\s+install|brew\s+install)\b|\b(?:requirements|dependencies)\b",
    "network": r"\b(?:curl|wget|ssh|scp|rsync|nc|netcat)\b|\brequests\.|\bhttpx\.|urllib\.request|\.(?:post|put|send|sendall|urlopen)\s*\(",
    "tls": r"--insecure|--no-check-certificate|\bcurl\s+[^\n]*\s-[a-z]*k\b|verify\s*=\s*False|CERT_NONE|_create_unverified_context",
    "destructive": r"\b(?:rm|chmod|chown|mkfs|dd)\b|shutil\.rmtree|\bgit\s+(?:reset|clean|restore)\b|\bgit\s+push\b.*(?:--force|-f\b)|\b(?:DROP|TRUNCATE)\s+(?:TABLE|DATABASE)\b|\b(?:eval|exec)\s*\(|os\.system|subprocess\.",
}
COMPILED = {name: re.compile(pattern, re.IGNORECASE) for name, pattern in PATTERNS.items()}


def classify(path, text):
    signals = []
    if path == "AGENTS.md" or path.startswith((".github/", "scripts/", "templates/")):
        signals.append("critical-file")
    if path.endswith(("requirements-ci.txt", "requirements.txt", "pyproject.toml", "package.json", "go.mod")):
        signals.append("dependency")
    signals.extend(name for name, pattern in COMPILED.items() if pattern.search(text))
    return sorted(set(signals))


def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", "--literal-pathspecs", *args], text=True, encoding="utf-8", errors="replace", timeout=30,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.base) or args.base == "0" * 40:
        parser.error("base должен быть SHA существующего коммита")
    git("cat-file", "-e", args.base + "^{commit}")
    # NUL разделяет имена, поэтому перевод строки или shell-метасимволы в имени безопасны.
    names = git("diff", "--no-ext-diff", "--no-textconv", "--name-only", "-z", args.base, "HEAD", "--").split("\0")
    totals = Counter()
    for path in filter(None, names):
        patch = git("diff", "--no-ext-diff", "--no-textconv", "--unified=0", args.base, "HEAD", "--", path)
        if len(patch.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("Diff файла больше 2 MiB: требуется отдельное ревью")
        hits = {name: [] for name in classify(path, "")}
        line = 0
        for row in patch.splitlines():
            hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", row)
            if hunk:
                line = int(hunk[1])
            elif row.startswith("+") and not row.startswith("+++"):
                for name in classify(path, row[1:]):
                    hits.setdefault(name, []).append(line)
                line += 1
        for name, locations in sorted(hits.items()):
            totals[name] += 1
            # Не выводим исходный текст, HTML или workflow-команды из PR.
            print(json.dumps({"path": path, "signal": name, "lines": locations[:20],
                              "additional_lines": max(0, len(locations) - 20)}, ensure_ascii=True))
    print(json.dumps({"review_signal_files": dict(totals), "blocking": False}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        sys.exit(1)
