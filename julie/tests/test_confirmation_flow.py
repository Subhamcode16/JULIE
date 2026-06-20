import unittest
import json
import uuid

from core.router import IntentType, ClassifiedIntent
from core.main import app, pending_actions
from starlette.testclient import TestClient


class ConfirmationFlowTestCase(unittest.TestCase):
    def test_yellow_action_creates_pending(self):
        # Simulate a YELLOW action by sending 'write file' intent which maps to write_file
        payload = {
            "type": "USER_INPUT_TEXT",
            "id": str(uuid.uuid4()),
            "payload": {"text": "write file D:\\tmp\\x.txt", "session_id": "s1"},
        }
        with TestClient(app) as client:
            with client.websocket_connect("/ws") as ws:
                ws.send_text(json.dumps(payload))
                msg = ws.receive_json()
                self.assertIn("needs_confirmation", msg["payload"])
                action_id = msg["payload"].get("action_id")
                self.assertTrue(action_id in pending_actions)

    def test_confirm_action_executes_or_cancels(self):
        # Create a fake pending action (we cancel it)
        fake_intent = ClassifiedIntent(
            intent_type=IntentType.SYSTEM_ACTION,
            confidence=0.9,
            params={"action": "write", "target": "C:\\tmp\\x.txt"},
            raw_input="write file C:\\tmp\\x.txt",
        )
        aid = str(uuid.uuid4())
        pending_actions[aid] = {"classified": fake_intent, "payload": {"session_id": "s1"}}

        try:
            with TestClient(app) as client:
                with client.websocket_connect("/ws") as ws:
                    ws.send_text(
                        json.dumps(
                            {
                                "type": "CONFIRM_ACTION",
                                "id": str(uuid.uuid4()),
                                "payload": {"action_id": aid, "decision": "cancel"},
                            }
                        )
                    )
                    msg = ws.receive_json()
                    self.assertEqual(msg["payload"]["response"], "Cancelled")
        finally:
            pending_actions.pop(aid, None)

    def test_confirm_action_executes_pending_intent(self):
        # Create a fake pending action that should execute a supported tool path.
        # execute_intent() supports SYSTEM_ACTION with action == 'terminal' and target == command.
        fake_intent = ClassifiedIntent(
            intent_type=IntentType.SYSTEM_ACTION,
            confidence=0.9,
            params={"action": "terminal", "target": "echo hello"},
            raw_input="run echo hello in terminal",
        )
        aid = str(uuid.uuid4())
        pending_actions[aid] = {"classified": fake_intent, "payload": {"session_id": "s1"}}

        try:
            with TestClient(app) as client:
                with client.websocket_connect("/ws") as ws:
                    ws.send_text(
                        json.dumps(
                            {
                                "type": "CONFIRM_ACTION",
                                "id": str(uuid.uuid4()),
                                "payload": {"action_id": aid, "decision": "confirm"},
                            }
                        )
                    )
                    msg = ws.receive_json()

                    self.assertTrue(msg["payload"]["success"])
                    response_payload = msg["payload"]["response"]
                    # For confirm->execute, core returns the raw tool result as `response`.
                    # run_terminal_command returns a dict with stdout.
                    self.assertIsInstance(response_payload, dict)
                    self.assertEqual(response_payload.get("stdout").strip().lower(), "hello")
        finally:
            pending_actions.pop(aid, None)


if __name__ == "__main__":
    unittest.main()

