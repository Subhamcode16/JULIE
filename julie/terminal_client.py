import argparse
import asyncio
import json
import uuid

import websockets


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
DEFAULT_SESSION_ID = "terminal"


def build_user_input_message(text: str, session_id: str = DEFAULT_SESSION_ID, source: str = "terminal") -> dict:
    return {
        "type": "USER_INPUT_TEXT",
        "id": str(uuid.uuid4()),
        "payload": {
            "text": text,
            "session_id": session_id,
            "source": source,
        },
    }


def build_confirm_action_message(action_id: str, decision: str) -> dict:
    return {
        "type": "CONFIRM_ACTION",
        "id": str(uuid.uuid4()),
        "payload": {
            "action_id": action_id,
            "decision": decision,
        },
    }


def format_response(message: dict) -> str:
    payload = message.get("payload", {})
    response_text = payload.get("response")
    if response_text is None:
        response_text = json.dumps(payload, indent=2)
    lines = [f"[{message.get('type')}] {response_text}"]

    if isinstance(payload.get("detail"), dict):
        lines.append("Details:")
        lines.append(json.dumps(payload["detail"], indent=2))

    if payload.get("needs_confirmation"):
        lines.append("⚠️ Confirmation required. Use the terminal prompt to confirm or cancel.")

    return "\n".join(lines)


async def interact(uri: str, session_id: str) -> None:
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}. Type 'exit' or Ctrl-D to quit.")

        while True:
            try:
                text = input("> ").strip()
            except EOFError:
                print("\nClosing connection.")
                break

            if not text:
                continue
            if text.lower() in {"exit", "quit"}:
                break

            user_msg = build_user_input_message(text, session_id=session_id)
            await websocket.send(json.dumps(user_msg))
            reply = json.loads(await websocket.recv())
            print(format_response(reply))

            if reply.get("payload", {}).get("needs_confirmation"):
                decision = input("Confirm action? [y/N]: ").strip().lower()
                if decision in {"y", "yes"}:
                    confirm_payload = build_confirm_action_message(reply["payload"]["action_id"], "confirm")
                else:
                    confirm_payload = build_confirm_action_message(reply["payload"]["action_id"], "cancel")
                await websocket.send(json.dumps(confirm_payload))
                confirm_reply = json.loads(await websocket.recv())
                print(format_response(confirm_reply))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Julie terminal WebSocket client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Julie WebSocket host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Julie WebSocket port")
    parser.add_argument("--session-id", default=DEFAULT_SESSION_ID, help="Session ID for conversation state")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    uri = f"ws://{args.host}:{args.port}/ws"
    try:
        asyncio.run(interact(uri, args.session_id))
    except KeyboardInterrupt:
        print("\nInterrupted; exiting.")
    except Exception as exc:
        print(f"Error connecting to Julie: {exc}")


if __name__ == "__main__":
    main()
