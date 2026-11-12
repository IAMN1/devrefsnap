import os
import unittest

from app import database_status


class DatabaseStatusTest(unittest.TestCase):
    def test_reports_current_database(self):
        status = database_status()
        expected_database = "compose_lab"
        if os.environ.get("LAB_FORCE_FAILURE") == "1":
            expected_database = "intentional_failure"

        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["database"], expected_database)
