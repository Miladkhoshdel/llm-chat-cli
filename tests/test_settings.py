import unittest

from llm.settings import Settings


class SettingsTests(unittest.TestCase):
    def make_settings(self, **overrides):
        values = {
            "api_key": "secret",
            "base_url": "https://example.com/v1",
            "model_name": "example-model",
            "show_usage": True,
            "max_tokens": 1000,
            "max_context_tokens": 8192,
            "temperature": 0.2,
            "top_p": 1.0,
            "memory_keep_count": 10,
        }
        values.update(overrides)
        return Settings(**values)

    def test_calculates_input_token_budget(self):
        settings = self.make_settings()

        self.assertEqual(settings.input_token_budget, 7192)

    def test_rejects_non_positive_output_limit(self):
        with self.assertRaisesRegex(ValueError, "MAX_TOKENS"):
            self.make_settings(max_tokens=0)

    def test_rejects_non_positive_context_limit(self):
        with self.assertRaisesRegex(ValueError, "MAX_CONTEXT_TOKENS"):
            self.make_settings(max_context_tokens=0)

    def test_rejects_output_limit_equal_to_context_limit(self):
        with self.assertRaisesRegex(ValueError, "must be smaller"):
            self.make_settings(max_tokens=8192)

    def test_rejects_negative_memory_limit(self):
        with self.assertRaisesRegex(ValueError, "must be 0 or greater"):
            self.make_settings(memory_keep_count=-1)

    def test_api_key_is_hidden_from_representation(self):
        settings = self.make_settings()

        self.assertNotIn("secret", repr(settings))


if __name__ == "__main__":
    unittest.main()
