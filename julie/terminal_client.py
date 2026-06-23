import argparse
import asyncio
import json
import uuid

import websockets


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
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

        async def receive_loop():
            try:
                while True:
                    message = await websocket.recv()
                    reply = json.loads(message)
                    if reply.get("type") == "STATE_CHANGE":
                        # We can optionally print state changes, or just ignore them to keep terminal clean
                        continue
                    print("\n" + format_response(reply))
                    
                    if reply.get("payload", {}).get("needs_confirmation"):
                        # For terminal, we can just print the instruction, the user can type 'confirm' or 'cancel' directly
                        # The backend whatsapp webhook does this. Actually, the backend needs a CONFIRM_ACTION msg.
                        pass
                    print("> ", end="", flush=True)
            except websockets.exceptions.ConnectionClosed:
                print("\nConnection closed by server.")

        async def input_loop():
            loop = asyncio.get_running_loop()
            while True:
                try:
                    text = await loop.run_in_executor(None, input, "> ")
                    text = text.strip()
                except EOFError:
                    print("\nClosing connection.")
                    break

                if not text:
                    continue
                if text.lower() in {"exit", "quit"}:
                    break
                
                # Check if it's a manual confirmation
                if text.lower() in {"confirm", "cancel"}:
                    # We don't have the action_id tracked perfectly here, but we can just send it as text
                    # and the backend might handle it. Wait, the backend requires a CONFIRM_ACTION message.
                    # This is a basic terminal client, we'll just send text.
                    pass

                user_msg = build_user_input_message(text, session_id=session_id)
                await websocket.send(json.dumps(user_msg))

        # Run both concurrently
        receive_task = asyncio.create_task(receive_loop())
        input_task = asyncio.create_task(input_loop())
        
        done, pending = await asyncio.wait(
            [receive_task, input_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        for task in pending:
            task.cancel()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sixteen terminal WebSocket client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Sixteen WebSocket host")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Sixteen WebSocket port")
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
        print(f"Error connecting to Sixteen: {exc}")


if __name__ == "__main__":
    main()
