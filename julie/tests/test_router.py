import unittest

from core.router import classify_intent, IntentType


class RouterTestCase(unittest.TestCase):
    def test_open_application_intent(self):
        result = classify_intent("open chrome")
        self.assertEqual(result.intent_type, IntentType.SYSTEM_ACTION)
        self.assertEqual(result.params.get("action"), "open")
        self.assertEqual(result.params.get("target"), "chrome")

    def test_navigate_intent(self):
        result = classify_intent("go to github.com")
        self.assertEqual(result.intent_type, IntentType.BROWSER_ACTION)
        self.assertEqual(result.params.get("url_or_query"), "github.com")

    def test_unknown_intent_defaults_to_conversation(self):
        result = classify_intent("what is the weather")
        self.assertEqual(result.intent_type, IntentType.CONVERSATION)
        self.assertEqual(result.params.get("query"), "what is the weather")


if __name__ == "__main__":
    unittest.main()
