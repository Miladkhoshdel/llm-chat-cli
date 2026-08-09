import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from code_review.flake8_runner import (
    Flake8ExecutionError,
    Flake8Runner,
)


class Flake8RunnerTests(unittest.TestCase):
    def test_parses_flake8_output(self):
        output = "./example.py\t3\t8\tF821\tundefined name 'value'\n"

        findings = Flake8Runner.parse_output(output)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path, "example.py")
        self.assertEqual(findings[0].line, 3)
        self.assertEqual(findings[0].column, 8)
        self.assertEqual(findings[0].code, "F821")
        self.assertEqual(findings[0].message, "undefined name 'value'")

    def test_returns_findings_when_flake8_reports_issues(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="./example.py\t1\t1\tF401\t'os' imported but unused\n",
            stderr="",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.flake8_runner.subprocess.run",
                return_value=completed,
            ) as run:
                findings = Flake8Runner().run(directory)

        self.assertEqual(findings[0].code, "F401")
        self.assertEqual(
            run.call_args.kwargs["cwd"],
            Path(directory).resolve(),
        )
        self.assertFalse(run.call_args.kwargs["check"])

    def test_returns_empty_list_for_clean_directory(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.flake8_runner.subprocess.run",
                return_value=completed,
            ):
                findings = Flake8Runner().run(directory)

        self.assertEqual(findings, [])

    def test_raises_when_flake8_fails_without_findings(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="",
            stderr="No module named flake8",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.flake8_runner.subprocess.run",
                return_value=completed,
            ):
                with self.assertRaisesRegex(
                    Flake8ExecutionError,
                    "No module",
                ):
                    Flake8Runner().run(directory)

    def test_rejects_missing_directory(self):
        with self.assertRaisesRegex(ValueError, "does not exist"):
            Flake8Runner().run("missing-review-directory")

    def test_rejects_malformed_output(self):
        with self.assertRaisesRegex(Flake8ExecutionError, "Could not parse"):
            Flake8Runner.parse_output("not valid flake8 output")


if __name__ == "__main__":
    unittest.main()
