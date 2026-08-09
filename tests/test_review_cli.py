import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import Mock, patch

import review
from llm import LLMResponse


class ReviewCliTests(unittest.TestCase):
    @patch("review.LLM")
    @patch("review.CodeReviewer")
    @patch("review.load_settings")
    def test_streams_review_after_finding_count_without_duplicate_output(
        self,
        load_settings,
        code_reviewer,
        llm,
    ):
        load_settings.return_value = SimpleNamespace(show_usage=False)
        findings = [Mock()]
        response = LLMResponse(
            content="Summary: one issue",
            finish_reason="stop",
        )

        def stream_review(directory, on_text, on_findings):
            on_findings(findings)
            on_text("Summary: ")
            on_text("one issue")
            return findings, response

        reviewer = code_reviewer.return_value
        reviewer.review.side_effect = stream_review
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = review.main(["."])

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            output.getvalue(),
            "Flake8 found 1 issue(s).\n\nSummary: one issue\n",
        )
        llm.assert_called_once_with(load_settings.return_value)


if __name__ == "__main__":
    unittest.main()
