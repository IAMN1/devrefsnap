#!/usr/bin/env python3
"""Статический разбор материалов. Учебный код никогда не исполняется."""
import argparse
import ast
from collections import Counter, defaultdict
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt

LANGUAGES = frozenset(
    "python py bash sh shell console text plaintext sql psql json yaml yml toml ini "
    "dockerfile go mermaid markdown md diff html css javascript js typescript ts "
    "xml http nginx makefile env powershell c cpp csharp cmake".split()
)
IGNORED_DIRS = frozenset({".git", ".venv", "__pycache__"})
MAX_FILE_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_FILES = 2000
PARSER = MarkdownIt("commonmark").enable("table")


def emit(row):
    # Runner принимает legacy ##[...] даже внутри JSON-строки.
    print(json.dumps(row, ensure_ascii=True).replace("#", r"\u0023"))


class HTMLTargets(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.anchors = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        names = {attrs.get("id")}
        if tag == "a":
            names.add(attrs.get("name"))
        line = self.getpos()[0]
        self.anchors.extend((line, name) for name in sorted(filter(None, names)))
        for key in ("href", "src"):
            if attrs.get(key):
                self.links.append((line, attrs[key]))


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
    anchors, links, seen = defaultdict(list), [], set()
    for index, token in enumerate(tokens):
        line = token.map[0] + 1 if token.map else 1
        if token.type == "heading_open":
            base = slug(inline_text(tokens[index + 1].children or []))
            anchor, suffix = base, 0
            while anchor in seen:
                suffix += 1
                anchor = f"{base}-{suffix}"
            seen.add(anchor)
            anchors[anchor].append(line)
        children = token.children or [token]
        for child in children:
            if child.type in {"link_open", "image"}:
                links.append((line, child.attrGet("href") or child.attrGet("src")))
            elif child.type in {"html_inline", "html_block"}:
                html = HTMLTargets()
                html.feed(child.content)
                for html_line, name in html.anchors:
                    anchors[name].append(line + html_line - 1)
                links.extend((line + html_line - 1, link) for html_line, link in html.links)
    return tokens, anchors, links


def check(root):
    root = root.resolve()
    examples = root / "examples"
    issues, pages, counts = [], {}, Counter()
    file_paths = set()

    def issue(path, line, code, message):
        issues.append(dict(path=str(path.relative_to(root)), line=line, code=code, message=message))

    def check_python(path, source, first_line, *, flags=0):
        try:
            compile(source, "<example>", "exec", flags=flags, dont_inherit=True)
        except (SyntaxError, ValueError) as error:
            line = first_line + (getattr(error, "lineno", 1) or 1) - 1
            issue(path, line, "python-syntax", str(error))

    def check_bash(path, source, first_line):
        try:
            result = subprocess.run(
                ["/bin/bash", "--noprofile", "--norc", "-n"],
                input=source, capture_output=True, text=True,
                env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"}, timeout=5,
            )
            if result.returncode:
                issue(path, first_line, "bash-syntax", result.stderr.strip())
        except subprocess.TimeoutExpired:
            issue(path, first_line, "bash-syntax", "Превышен предел разбора Bash: 5 секунд")

    def walk(directory):
        for path in sorted(directory.iterdir()):
            if path.name in IGNORED_DIRS:
                continue
            if path.is_symlink():
                issue(path, 1, "symlink", "Символьные ссылки не поддерживаются проверкой")
            elif path.is_dir():
                yield from walk(path)
            elif path.is_file():
                file_paths.add(path.as_posix())
                if path.suffix.lower() == ".md" or (path.suffix in {".py", ".sh"} and path.is_relative_to(examples)):
                    yield path

    total_bytes = 0
    for path in walk(root):
        is_python_file = path.suffix == ".py"
        is_shell_file = path.suffix == ".sh"
        kind = "python_files" if is_python_file else "bash_files" if is_shell_file else "markdown"
        counts[kind] += 1
        size = path.stat().st_size
        total_bytes += size
        if counts["markdown"] + counts["python_files"] + counts["bash_files"] > MAX_FILES or total_bytes > MAX_TOTAL_BYTES:
            issue(path, 1, "limit", "Превышен общий предел объёма материалов")
            break
        if size > MAX_FILE_BYTES:
            issue(path, 1, "limit", "Файл материала больше 1 MiB")
            continue
        if is_python_file:
            check_python(path, path.read_bytes(), 1)
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            issue(path, 1, "encoding", "Ожидается UTF-8")
            continue
        if is_shell_file:
            check_bash(path, text, 1)
            continue
        tokens, anchors, links = parse_page(text)
        pages[path] = (anchors, links)
        for name, lines in anchors.items():
            for line in lines[1:]:
                issue(path, line, "duplicate-anchor", f"Якорь {name!r} уже задан в строке {lines[0]}")
        for token in tokens:
            if token.type != "fence":
                continue
            counts["fences"] += 1
            line = token.map[0] + 1
            # При закрытии диапазон содержит opener + content + closer.
            # Префиксы цитат и списков уже разобраны Markdown-парсером.
            content_lines = token.content.count("\n") + bool(token.content and not token.content.endswith("\n"))
            if token.map[1] - token.map[0] != content_lines + 2:
                issue(path, line, "fence-close", "Ограждение кода не закрыто")
            language = token.info.strip().split()[0] if token.info.strip() else ""
            if language not in LANGUAGES:
                issue(path, line, "fence-language", f"Неизвестный или отсутствующий язык: {language!r}")
            if language in {"python", "py"}:
                counts["python"] += 1
                check_python(path, token.content, line + 1, flags=ast.PyCF_ALLOW_TOP_LEVEL_AWAIT)
            elif language in {"bash", "sh", "shell"}:
                counts["bash"] += 1
                check_bash(path, token.content, line)

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
            target = path
            if url.path:
                decoded = unquote(url.path)
                target = root / decoded.lstrip("/") if decoded.startswith("/") else path.parent / decoded
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
                target = target / "README.md"
                resolved = resolved / "README.md"
            if Path(os.path.normpath(target)).as_posix() not in file_paths:
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
        emit(row)
    emit({"status": "failed" if issues else "passed", **counts, "errors": len(issues)})
    return bool(issues)


if __name__ == "__main__":
    sys.exit(main())
