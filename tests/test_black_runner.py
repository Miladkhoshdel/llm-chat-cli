import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from code_review.black_runner import BlackExecutionError, BlackRunner


class BlackRunnerTests(unittest.TestCase):
    def test_parses_black_diff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            output = (
                f"--- {root}/example.py\t2026-01-01 00:00:00+00:00\n"
                f"+++ {root}/example.py\t2026-01-01 00:00:01+00:00\n"
                "@@ -1 +1 @@\n"
                "-x={1:2}\n"
                "+x = {1: 2}\n"
            )

            findings = BlackRunner.parse_output(output, root)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].path, "example.py")
        self.assertEqual(findings[0].code, "BLACK")
        self.assertIsNone(findings[0].line)

    def test_returns_findings_when_black_would_reformat(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=1,
            stdout="--- example.py\told\n+++ example.py\tnew\n@@ -1 +1 @@\n",
            stderr="would reformat example.py",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.black_runner.subprocess.run",
                return_value=completed,
            ) as run:
                findings = BlackRunner().run(directory)

        self.assertEqual(findings[0].path, "example.py")
        self.assertIn("--check", run.call_args.args[0])
        self.assertIn("--diff", run.call_args.args[0])
        self.assertFalse(run.call_args.kwargs["check"])

    def test_returns_empty_list_for_clean_directory(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="",
            stderr="All done!",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.black_runner.subprocess.run",
                return_value=completed,
            ):
                findings = BlackRunner().run(directory)

        self.assertEqual(findings, [])

    def test_raises_when_black_fails(self):
        completed = subprocess.CompletedProcess(
            args=[],
            returncode=123,
            stdout="",
            stderr="Black failed to format a file",
        )

        with tempfile.TemporaryDirectory() as directory:
            with patch(
                "code_review.black_runner.subprocess.run",
                return_value=completed,
            ):
                with self.assertRaisesRegex(BlackExecutionError, "failed"):
                    BlackRunner().run(directory)


if __name__ == "__main__":
    unittest.main()
