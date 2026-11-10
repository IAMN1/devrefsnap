"""Проверки наблюдаемого поведения CLI на синтетическом Markdown."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CHECKER = Path(__file__).resolve().parents[1] / "check_materials.py"


class MaterialsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def check(self, expected=0, code=None, env=None):
        run = subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root)],
            capture_output=True, text=True, timeout=20, env=env,
        )
        self.assertEqual(run.returncode, expected, run.stdout + run.stderr)
        rows = [json.loads(line) for line in run.stdout.splitlines()]
        if code:
            self.assertIn(code, [row.get("code") for row in rows], rows)
        return rows

    def test_russian_duplicate_headings_inline_code_and_reference_links(self):
        self.write("README.md", "[цель][target]\n\n[target]: <тема (1).md#пример-api-1>\n")
        self.write("тема (1).md", "# Пример `API`\n# Пример API\n[назад](README.md)\n")
        self.check()

    def test_missing_file_fails(self):
        self.write("README.md", "[пример](missing.md)\n")
        self.check(1, "link")

    def test_missing_anchor_fails(self):
        self.write("README.md", "# Тема\n[ошибка](#нет)\n")
        self.check(1, "anchor")

    def test_html_anchor_and_image_target(self):
        self.write("README.md", '<a id="demo"></a>\n\n[пример](#demo)\n![img](image.svg)\n')
        self.write("image.svg", "<svg/>")
        self.check()

    def test_external_urls_are_not_requested(self):
        self.write("README.md", "[нет сети](https://does-not-exist.invalid/nope#abc)\n")
        self.check()

    def test_link_cannot_escape_root(self):
        self.write("README.md", "[outside](../outside.md)\n")
        self.check(1, "link-boundary")

    def test_symlink_not_followed(self):
        outside = self.root.parent / (self.root.name + "-outside.md")
        outside.write_text("# Outside\n")
        self.addCleanup(outside.unlink)
        (self.root / "linked.md").symlink_to(outside)
        self.write("README.md", "[outside](linked.md)\n")
        self.check(1, "symlink")

    def test_missing_fence_language_and_unclosed_fence_fail(self):
        self.write("README.md", "```\nx\n```\n\n```python\nx = 1\n")
        self.check(1, "fence-language")
        self.check(1, "fence-close")

    def test_lone_bare_fence_is_not_its_own_closing_fence(self):
        self.write("README.md", "```\n")
        self.check(1, "fence-close")

    def test_large_file_is_rejected(self):
        self.write("README.md", "x" * (1024 * 1024 + 1))
        self.check(1, "limit")

    def test_unknown_fence_language_fails(self):
        self.write("README.md", "```pythno\nx = 1\n```\n")
        self.check(1, "fence-language")

    def test_long_fence_contains_example_fence_and_crlf(self):
        self.write("README.md", "````markdown\r\n```python\r\nx = 1\r\n```\r\n````\r\n")
        self.check()

    def test_false_closer_inside_fence_is_rejected(self):
        for last in ("> ```", "    ```"):
            with self.subTest(last=last):
                self.write("README.md", "```text\nhello\n" + last + "\n")
                self.check(1, "fence-close")

    def test_unicode_line_separator_is_content_and_eof_without_newline_is_not_a_closer(self):
        self.write("README.md", "```text\na\u2028b\n```\n")
        self.check()
        self.write("README.md", "```text\nhello")
        self.check(1, "fence-close")

    def test_real_blockquote_and_list_fences_are_accepted(self):
        self.write("README.md", "> ```text\n> hello\n> ```\n\n- Item\n\n  ```text\n  hello\n  ```\n")
        self.check()

    def test_legacy_workflow_command_in_filename_is_escaped(self):
        for name in ("##[error]INJECTED.md", "##[add-mask]INJECTED.md", "##[stop-commands]INJECTED.md"):
            self.write(name, "```bad##[error]INJECTED\nexample\n```\n")
        run = subprocess.run([sys.executable, str(CHECKER), "--root", str(self.root)],
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 1)
        self.assertNotIn("##[", run.stdout)
        rows = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual({row["path"] for row in rows if "path" in row},
                         {"##[error]INJECTED.md", "##[add-mask]INJECTED.md", "##[stop-commands]INJECTED.md"})

    def test_python_syntax_error_fails(self):
        self.write("README.md", "```python\ndef broken(:\n    pass\n```\n")
        self.check(1, "python-syntax")

    def test_top_level_await_is_valid_fragment(self):
        self.write("README.md", "```python\nawait client.get('item')\n```\n")
        self.check()

    def test_bash_syntax_error_fails(self):
        self.write("README.md", "```bash\nif true; then\n```\n")
        self.check(1, "bash-syntax")

    def test_python_and_bash_payloads_and_bash_env_are_not_executed(self):
        marker = self.root / "EXECUTED"
        init = self.write("evil-env", f"touch '{marker}'\n")
        self.write("README.md", (
            f"```python\nfrom pathlib import Path\nPath({str(marker)!r}).touch()\n```\n"
            f"```bash\ntouch '{marker}'\nx=$(touch '{marker}')\n"
            f"cat <(touch '{marker}')\n```\n"
        ))
        env = dict(os.environ, BASH_ENV=str(init), ENV=str(init))
        self.check(env=env)
        self.assertFalse(marker.exists(), "Недоверенный код был исполнен")


if __name__ == "__main__":
    unittest.main()
