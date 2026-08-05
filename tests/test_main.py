import unittest

from main import trim_history


class TrimHistoryTests(unittest.TestCase):
    def setUp(self):
        self.messages = [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "one"},
            {"role": "assistant", "content": "first"},
            {"role": "user", "content": "two"},
            {"role": "assistant", "content": "second"},
            {"role": "user", "content": "three"},
            {"role": "assistant", "content": "third"},
        ]

    def test_keeps_system_message_and_latest_exchanges(self):
        result = trim_history(self.messages, 2)

        self.assertEqual(result, [self.messages[0], *self.messages[3:]])

    def test_zero_keeps_only_system_message(self):
        self.assertEqual(trim_history(self.messages, 0), self.messages[:1])

    def test_large_limit_keeps_all_messages(self):
        self.assertEqual(trim_history(self.messages, 10), self.messages)

    def test_negative_limit_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "must be 0 or greater"):
            trim_history(self.messages, -1)


if __name__ == "__main__":
    unittest.main()
