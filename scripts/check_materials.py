#!/usr/bin/env python3
"""Статический разбор материалов. Учебный код никогда не исполняется."""
import argparse
import ast
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

LANGUAGES = frozenset("python py bash sh shell console text plaintext sql psql json yaml yml toml ini dockerfile go mermaid markdown md diff html css javascript js typescript ts xml http nginx makefile env powershell".split())
IGNORED_DIRS = frozenset({".git", ".venv", "__pycache__"})
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_FILES = 2000
PARSER = MarkdownIt("commonmark").enable("table")


class HTMLTargets(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = set()
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("id", "name" if tag == "a" else "id"):
            if attrs.get(key):
                self.anchors.add(attrs[key])
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append(attrs[key])


def slug(text):
    """GitHub-подобный якорь для заголовков текущих материалов."""
    return "".join(
        char for char in text.lower()
        if char in "-_ " or unicodedata.category(char)[0] in "LNM"
    ).replace(" ", "-")


def inline_text(tokens):
    return "".join(
        inline_text(token.children) if token.children else token.content
        for token in tokens
        if token.type in {"text", "code_inline", "image", "softbreak", "hardbreak"}
    )


def parse_page(text):
    tokens = PARSER.parse(text)
    anchors, links, seen = set(), [], set()
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            base = slug(inline_text(tokens[index + 1].children or []))
            anchor, suffix = base, 0
            while anchor in seen:
                suffix += 1
                anchor = f"{base}-{suffix}"
            seen.add(anchor)
            anchors.add(anchor)
        children = token.children or [token]
        for child in children:
            if child.type in {"link_open", "image"}:
                links.append((token.map[0] + 1 if token.map else 1,
                              child.attrGet("href") or child.attrGet("src")))
            elif child.type in {"html_inline", "html_block"}:
                html = HTMLTargets()
                html.feed(child.content)
                anchors.update(html.anchors)
                links.extend((token.map[0] + 1 if token.map else 1, link) for link in html.links)
    return tokens, anchors, links


def check(root):
    root = root.resolve()
    issues, pages, counts = [], {}, Counter()

    def issue(path, line, code, message):
        issues.append(dict(path=str(path.relative_to(root)), line=line, code=code, message=message))

    def walk(directory):
        for path in sorted(directory.iterdir()):
            if path.name in IGNORED_DIRS:
                continue
            if path.is_symlink():
                issue(path, 1, "symlink", "Символьные ссылки не поддерживаются проверкой")
            elif path.is_dir():
                yield from walk(path)
            elif path.suffix.lower() == ".md":
                yield path

    total_bytes = 0
    for path in walk(root):
        counts["markdown"] += 1
        size = path.stat().st_size
        total_bytes += size
        if counts["markdown"] > MAX_FILES or total_bytes > MAX_TOTAL_BYTES:
            issue(path, 1, "limit", "Превышен общий предел объёма Markdown")
            break
        if size > MAX_FILE_BYTES:
            issue(path, 1, "limit", "Markdown-файл больше 1 MiB")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            issue(path, 1, "encoding", "Ожидается UTF-8")
            continue
        tokens, anchors, links = parse_page(text)
        pages[path] = (anchors, links)
        lines = text.splitlines()
        for token in tokens:
            if token.type != "fence":
                continue
            counts["fences"] += 1
            line = token.map[0] + 1
            last = lines[token.map[1] - 1].lstrip(" >\t").rstrip()
            if token.map[1] <= token.map[0] + 1 or not re.fullmatch(re.escape(token.markup[0]) + "{" + str(len(token.markup)) + ",}", last):
                issue(path, line, "fence-close", "Ограждение кода не закрыто")
            language = token.info.strip().split()[0] if token.info.strip() else ""
            if language not in LANGUAGES:
                issue(path, line, "fence-language", f"Неизвестный или отсутствующий язык: {language!r}")
            if language in {"python", "py"}:
                counts["python"] += 1
                try:
                    compile(token.content, "<markdown>", "exec", flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT, dont_inherit=True)
                except (SyntaxError, ValueError) as error:
                    issue(path, line + (getattr(error, "lineno", 1) or 1), "python-syntax", str(error))
            elif language in {"bash", "sh", "shell"}:
                counts["bash"] += 1
                try:
                    result = subprocess.run(
                        ["/bin/bash", "--noprofile", "--norc", "-n"],
                        input=token.content, capture_output=True, text=True,
                        env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}, timeout=5,
                    )
                    if result.returncode:
                        issue(path, line, "bash-syntax", result.stderr.strip())
                except subprocess.TimeoutExpired:
                    issue(path, line, "bash-syntax", "Превышен предел разбора Bash: 5 секунд")

    for path, (_, links) in pages.items():
        for line, link in links:
            counts["links"] += 1
            try:
                url = urlsplit(link)
            except ValueError:
                issue(path, line, "link", "Некорректный адрес ссылки")
                continue
            if url.scheme or url.netloc:
                continue  # Не обращаемся к сети.
            target = path.parent / unquote(url.path) if url.path else path
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                issue(path, line, "link-boundary", f"Ссылка за пределы репозитория: {link}")
                continue
            # Проверяем всю цепочку, включая символьный каталог внутри корня.
            parts = target.absolute().relative_to(root).parts
            probe = root
            if any((probe := probe / part).is_symlink() for part in parts):
                issue(path, line, "symlink", f"Ссылка через символический путь: {link}")
                continue
            if resolved.is_dir():
                resolved = resolved / "README.md"
            if not resolved.is_file():
                issue(path, line, "link", f"Не найден файл: {link}")
            elif url.fragment and resolved.suffix.lower() == ".md":
                if resolved not in pages or unquote(url.fragment) not in pages[resolved][0]:
                    issue(path, line, "anchor", f"Не найден якорь: {link}")
    return issues, dict(counts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    issues, counts = check(args.root)
    for row in issues:
        print(json.dumps(row, ensure_ascii=True))
    print(json.dumps({"status": "failed" if issues else "passed", **counts, "errors": len(issues)}))
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())
