"""Сигналы ревью не являются классификатором вредоносности."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "review_signals.py"


class SignalsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if SCRIPT.exists():
            spec = importlib.util.spec_from_file_location("review_signals", SCRIPT)
            cls.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.module)
        else:
            cls.module = None

    def signals(self, path, line):
        self.assertIsNotNone(self.module, "Проверяющий код отсутствует")
        return self.module.classify(path, line)

    def test_network_address_dependency_tls_and_destructive_command(self):
        for text, expected in [
            ("https://example.invalid/script.sh", "external-url"),
            ("python -m pip install example", "dependency"),
            ("requests.post(endpoint, data=payload)", "network"),
            ("curl --insecure https://example.invalid", "tls"),
            ("session.get(url, verify=False)", "tls"),
            ("rm -rf ./synthetic-data", "destructive"),
            ("git push --force origin main", "destructive"),
        ]:
            with self.subTest(text=text):
                self.assertIn(expected, self.signals("example.md", text))

    def test_critical_file_is_flagged_even_without_keywords(self):
        for path in (".github/CODEOWNERS", ".github/workflows/ci.yml", "scripts/a.py", "AGENTS.md", "templates/page.md"):
            self.assertIn("critical-file", self.signals(path, "simple change"))

    def test_normal_prose_does_not_trigger(self):
        self.assertEqual(self.signals("README.md", "Создайте таблицу для сравнения."), [])

    def test_diff_does_not_execute_payload_or_emit_raw_workflow_commands(self):
        self.assertTrue(SCRIPT.exists(), "Проверяющий код отсутствует")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            def git(*args):
                return subprocess.check_output(["git", *args], cwd=root, text=True).strip()
            git("init", "-q")
            git("config", "user.name", "CI test")
            git("config", "user.email", "ci@example.invalid")
            page = root / "README.md"
            page.write_text("# Example\n")
            git("add", ".")
            git("commit", "-qm", "base")
            base = git("rev-parse", "HEAD")
            marker = root / "EXECUTED"
            page.write_text(f"# Example\n::error::curl $(touch {marker})\nrm -rf synthetic\n")
            (root / ":(exclude)*").write_text("curl https://example.invalid\n")
            git("add", "--all")
            git("commit", "-qm", "change")
            run = subprocess.run([sys.executable, str(SCRIPT), "--base", base], cwd=root,
                                 capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 0, run.stderr)
            rows = [json.loads(line) for line in run.stdout.splitlines()]
            self.assertTrue(any(row.get("path") == ":(exclude)*" and row.get("signal") == "network" for row in rows))
            self.assertIn("network", run.stdout)
            self.assertIn("destructive", run.stdout)
            self.assertFalse(marker.exists())
            self.assertFalse(any(line.startswith("::") for line in run.stdout.splitlines()))
            bad = subprocess.run([sys.executable, str(SCRIPT), "--base", "--output=bad"],
                                 cwd=root, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
