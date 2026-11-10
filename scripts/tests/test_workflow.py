"""Регрессии границ CI. Проверка не заменяет доверенное ревью изменений самого CI."""
from pathlib import Path
import re
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[2]


class WorkflowTests(unittest.TestCase):
    def test_workflows_keep_untrusted_execution_unprivileged(self):
        workflows = list((ROOT / ".github/workflows").glob("*.y*ml"))
        self.assertEqual(len(workflows), 1, "Новый workflow требует пересмотра модели доступа")
        workflow = yaml.load(workflows[0].read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow["on"]), {"pull_request", "push"})
        self.assertEqual(workflow["on"]["pull_request"]["branches"], ["main"])
        self.assertEqual(workflow["on"]["push"]["branches"], ["main"])
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(set(workflow["jobs"]), {"materials-static", "checker-tests"})
        for name, job in workflow["jobs"].items():
            self.assertEqual(job["name"], name)
            self.assertEqual(job["runs-on"], "ubuntu-24.04")
            self.assertLessEqual(int(job["timeout-minutes"]), 5)
            for key in ("permissions", "secrets", "environment", "container", "services", "uses"):
                self.assertNotIn(key, job)
            checkout = []
            for step in job["steps"]:
                self.assertNotIn("secrets.", str(step))
                if "run" in step:
                    self.assertNotIn("${{", step["run"], "Контекст нельзя вставлять непосредственно в shell")
                if "uses" in step:
                    self.assertRegex(step["uses"], r"^actions/(checkout|setup-python)@[0-9a-f]{40}$")
                    if step["uses"].startswith("actions/checkout@"):
                        checkout.append(step)
                        self.assertEqual(step["with"]["persist-credentials"], "false")
                    else:
                        self.assertNotIn("cache", step.get("with", {}))
            self.assertEqual(len(checkout), 1)


if __name__ == "__main__":
    unittest.main()
