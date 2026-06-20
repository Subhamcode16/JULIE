import unittest

from core.router import ClassifiedIntent, IntentType
from core.tool_executor import execute_intent


class ToolExecutorTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_launch_application_fails_without_binary(self):
        intent = ClassifiedIntent(
            intent_type=IntentType.SYSTEM_ACTION,
            confidence=0.95,
            params={"action": "open", "target": "nonexistentapp123"},
            raw_input="open nonexistentapp123",
        )
        result = await execute_intent(intent)
        self.assertFalse(result["success"])
        self.assertIn("Could not locate application", result["error"])

    async def test_terminal_command_runs(self):
        intent = ClassifiedIntent(
            intent_type=IntentType.SYSTEM_ACTION,
            confidence=0.95,
            params={"action": "terminal", "target": "echo hello"},
            raw_input="run echo hello in terminal",
        )
        pending = await execute_intent(intent)
        self.assertFalse(pending["success"])
        self.assertTrue(pending["needs_confirmation"])

        result = await execute_intent(intent, confirmed=True)
        self.assertTrue(result["success"])
        self.assertEqual(result["detail"]["stdout"].strip(), "hello")


if __name__ == "__main__":
    unittest.main()
