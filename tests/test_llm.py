import unittest
from dataclasses import FrozenInstanceError

from llm import LLMResponse, LLMUsage


class LLMDataClassTests(unittest.TestCase):
    def test_response_contains_content_finish_reason_and_usage(self):
        usage = LLMUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            reasoning_tokens=2,
            cost=0.001,
        )

        response = LLMResponse(
            content="Hello",
            finish_reason="stop",
            usage=usage,
        )

        self.assertEqual(response.content, "Hello")
        self.assertEqual(response.finish_reason, "stop")
        self.assertEqual(response.usage, usage)

    def test_usage_is_optional(self):
        response = LLMResponse(content="Hello", finish_reason="stop")

        self.assertIsNone(response.usage)

    def test_response_is_immutable(self):
        response = LLMResponse(content="Hello", finish_reason="stop")

        with self.assertRaises(FrozenInstanceError):
            response.content = "Changed"


if __name__ == "__main__":
    unittest.main()
