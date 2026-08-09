from .flake8_runner import Flake8Runner
from .prompt import build_review_messages


class CodeReviewer:
    def __init__(self, llm, runner=None):
        self.llm = llm
        self.runner = runner or Flake8Runner()

    def review(self, directory, on_text=None):
        findings = self.runner.run(directory)

        if not findings:
            return findings, None

        messages = build_review_messages(directory, findings)
        response = self.llm.complete(messages, on_text=on_text)

        return findings, response
