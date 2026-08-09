import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from code_review.models import Flake8Finding
from code_review.prompt import build_review_messages
from code_review.reviewer import CodeReviewer
from llm import LLMResponse


class ReviewPromptTests(unittest.TestCase):
    def test_includes_finding_and_affected_source_line(self):
        finding = Flake8Finding(
            path="example.py",
            line=2,
            column=11,
            code="F821",
            message="undefined name 'missing_name'",
        )

        with tempfile.TemporaryDirectory() as directory:
            source_path = Path(directory) / "example.py"
            source_path.write_text(
                "def example():\n    print(missing_name)\n",
                encoding="utf-8",
            )

            messages = build_review_messages(directory, [finding])

        payload = messages[1]["content"].split("\n\n", 1)[1]
        finding_data = json.loads(payload)[0]
        self.assertEqual(finding_data["code"], "F821")
        self.assertEqual(finding_data["source"], "    print(missing_name)")

    def test_requests_compact_plain_text_without_markdown_tables(self):
        finding = Flake8Finding(
            path="example.py",
            line=1,
            column=1,
            code="F401",
            message="'os' imported but unused",
        )

        messages = build_review_messages(".", [finding])

        system_prompt = messages[0]["content"]
        user_prompt = messages[1]["content"]
        self.assertIn("compact plain text", system_prompt)
        self.assertIn("never use Markdown tables", system_prompt)
        self.assertIn("Group repeated findings", system_prompt)
        self.assertIn("at most three example", system_prompt)
        self.assertIn("do not enumerate every repeated path", system_prompt)
        self.assertIn("Keep each item on one logical line", system_prompt)
        self.assertIn("compact plain-text format", user_prompt)
        self.assertNotIn("Markdown report", user_prompt)


class CodeReviewerTests(unittest.TestCase):
    def test_does_not_call_llm_when_flake8_finds_nothing(self):
        runner = Mock()
        runner.run.return_value = []
        llm = Mock()
        reviewer = CodeReviewer(llm, runner=runner)

        findings, response = reviewer.review(".")

        self.assertEqual(findings, [])
        self.assertIsNone(response)
        llm.complete.assert_not_called()

    def test_sends_findings_to_llm(self):
        finding = Flake8Finding(
            path="example.py",
            line=1,
            column=1,
            code="F401",
            message="'os' imported but unused",
        )
        runner = Mock()
        runner.run.return_value = [finding]
        llm = Mock()
        expected_response = LLMResponse(
            content="Remove the unused import.",
            finish_reason="stop",
        )
        llm.complete.return_value = expected_response
        reviewer = CodeReviewer(llm, runner=runner)

        findings, response = reviewer.review(".")

        self.assertEqual(findings, [finding])
        self.assertEqual(response, expected_response)
        messages = llm.complete.call_args.args[0]
        self.assertIn("F401", messages[1]["content"])

    def test_reports_findings_before_calling_llm(self):
        finding = Flake8Finding(
            path="example.py",
            line=1,
            column=1,
            code="F401",
            message="'os' imported but unused",
        )
        events = []
        runner = Mock()
        runner.run.return_value = [finding]
        llm = Mock()
        llm.complete.side_effect = lambda messages, on_text: (
            events.append("llm")
            or LLMResponse(content="Remove it.", finish_reason="stop")
        )
        reviewer = CodeReviewer(llm, runner=runner)

        reviewer.review(
            ".",
            on_findings=lambda findings: events.append("findings"),
        )

        self.assertEqual(events, ["findings", "llm"])


if __name__ == "__main__":
    unittest.main()
