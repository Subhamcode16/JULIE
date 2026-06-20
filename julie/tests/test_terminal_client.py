import unittest
import json

from terminal_client import build_user_input_message, build_confirm_action_message, format_response


class TerminalClientTestCase(unittest.TestCase):
    def test_build_user_input_message(self):
        message = build_user_input_message("hello julie", session_id="test-session")
        self.assertEqual(message["type"], "USER_INPUT_TEXT")
        self.assertEqual(message["payload"]["text"], "hello julie")
        self.assertEqual(message["payload"]["session_id"], "test-session")
        self.assertEqual(message["payload"]["source"], "terminal")

    def test_build_confirm_action_message(self):
        action_id = "abc123"
        message = build_confirm_action_message(action_id, "confirm")
        self.assertEqual(message["type"], "CONFIRM_ACTION")
        self.assertEqual(message["payload"]["action_id"], action_id)
        self.assertEqual(message["payload"]["decision"], "confirm")

    def test_format_response_shows_payload(self):
        message = {
            "type": "USER_INPUT_TEXT_RESPONSE",
            "payload": {"response": "Done", "detail": {"stdout": "ok"}},
        }
        output = format_response(message)
        self.assertIn("[USER_INPUT_TEXT_RESPONSE] Done", output)
        self.assertIn("\"stdout\": \"ok\"", output)

    def test_format_response_hides_detail_when_missing(self):
        message = {"type": "HEALTH_CHECK_RESPONSE", "payload": {"status": "ok"}}
        output = format_response(message)
        self.assertIn("[HEALTH_CHECK_RESPONSE] {\n  \"status\": \"ok\"\n}", output)


if __name__ == "__main__":
    unittest.main()
