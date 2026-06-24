import asyncio
import json
import uuid
from datetime import datetime

import websockets
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Input, RichLog

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766

def build_user_input_message(text: str) -> dict:
    return {
        "type": "USER_INPUT_TEXT",
        "id": str(uuid.uuid4()),
        "payload": {
            "text": text,
            "session_id": "terminal",
            "source": "terminal",
        },
    }

class SixteenDashboard(App):
    TITLE = "Sixteen AI Terminal"
    
    CSS = """
    #chat-container {
        width: 70%;
        height: 1fr;
    }
    #status-container {
        width: 30%;
        height: 1fr;
        border-left: solid green;
    }
    #chat-log {
        height: 1fr;
        border: solid cyan;
    }
    #status-log {
        height: 1fr;
        border: solid magenta;
    }
    Input {
        dock: bottom;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="chat-container"):
                yield RichLog(id="chat-log", markup=True)
            with Vertical(id="status-container"):
                yield RichLog(id="status-log", markup=True)
        yield Input(placeholder="Type a message...", id="message-input")
        yield Footer()

    async def on_mount(self) -> None:
        self.chat_log = self.query_one("#chat-log", RichLog)
        self.status_log = self.query_one("#status-log", RichLog)
        self.input = self.query_one("#message-input", Input)
        
        self.chat_log.write("[bold cyan]Welcome to Sixteen Dashboard[/bold cyan]")
        self.status_log.write("[bold green]System Metrics Initialized[/bold green]")
        
        # Start websocket worker
        self.ws_task = asyncio.create_task(self.websocket_loop())

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        
        self.input.value = ""
        self.chat_log.write(f"[bold blue]You:[/bold blue] {text}")
        
        if hasattr(self, 'ws') and self.ws.open:
            msg = build_user_input_message(text)
            await self.ws.send(json.dumps(msg))
        else:
            self.chat_log.write("[bold red]Not connected to server.[/bold red]")

    async def websocket_loop(self):
        uri = f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}/ws"
        while True:
            try:
                self.status_log.write(f"Connecting to {uri}...")
                async with websockets.connect(uri) as ws:
                    self.ws = ws
                    self.status_log.write("[bold green]Connected![/bold green]")
                    while True:
                        response_str = await ws.recv()
                        await self.handle_message(response_str)
            except Exception as e:
                self.status_log.write(f"[bold red]Connection lost: {e}[/bold red]")
                await asyncio.sleep(3)
                
    async def handle_message(self, response_str: str):
        try:
            data = json.loads(response_str)
            msg_type = data.get("type", "")
            payload = data.get("payload", {})
            
            if msg_type == "STATE_CHANGE":
                state = payload.get("state", "UNKNOWN")
                self.status_log.write(f"Sixteen State: [bold yellow]{state}[/bold yellow]")
            elif msg_type == "USER_INPUT_TEXT_RESPONSE":
                reply = payload.get("response", "")
                self.chat_log.write(f"[bold magenta]Sixteen:[/bold magenta] {reply}")
            elif msg_type == "CONFIRM_ACTION":
                action_id = payload.get("action_id")
                question = payload.get("question")
                self.chat_log.write(f"[bold yellow][ACTION REQUIRED][/bold yellow] {question}")
            else:
                self.status_log.write(f"Received {msg_type}")
        except Exception as e:
            self.status_log.write(f"Error parsing msg: {e}")

if __name__ == "__main__":
    app = SixteenDashboard()
    app.run()
