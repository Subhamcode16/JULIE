"""Voice IPC client to connect Julie core with the voice pipeline."""

import json
import uuid
import asyncio
import websockets
from loguru import logger

from .speaker import speak

WS_URL = "ws://127.0.0.1:8766/ws"

class VoiceIPCClient:
    def __init__(self):
        self.ws = None
        self.running = False
        self._send_queue = asyncio.Queue()

    async def connect_and_listen(self):
        self.running = True
        while self.running:
            try:
                logger.info(f"Connecting to core at {WS_URL}...")
                async with websockets.connect(WS_URL) as ws:
                    self.ws = ws
                    logger.success("Connected to Julie core!")
                    
                    # Create tasks for reading and writing
                    read_task = asyncio.create_task(self._read_loop())
                    write_task = asyncio.create_task(self._write_loop())
                    
                    done, pending = await asyncio.wait(
                        [read_task, write_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in pending:
                        task.cancel()
            except Exception as e:
                logger.warning(f"Connection lost or failed: {e}. Retrying in 3 seconds...")
                await asyncio.sleep(3)
            finally:
                self.ws = None

    async def _read_loop(self):
        while True:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                msg_type = data.get("type")
                payload = data.get("payload", {})
                
                if msg_type == "USER_INPUT_VOICE_RESPONSE":
                    response_text = payload.get("response")
                    if response_text:
                        logger.info(f"Julie: {response_text}")
                        # Send to Kokoro TTS
                        speak(response_text)
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                logger.error(f"Error reading from WS: {e}")

    async def _write_loop(self):
        while True:
            try:
                message = await self._send_queue.get()
                await self.ws.send(message)
                self._send_queue.task_done()
            except Exception as e:
                logger.error(f"Error writing to WS: {e}")
                break

    def send_voice_input(self, transcript: str):
        """Send a transcribed string to the core."""
        msg = {
            "type": "USER_INPUT_VOICE",
            "id": str(uuid.uuid4()),
            "payload": {
                "text": transcript,
                "source": "voice",
                "session_id": "voice_session_1"
            }
        }
        try:
            self._send_queue.put_nowait(json.dumps(msg))
        except Exception as e:
            logger.error(f"Failed to queue voice input: {e}")

    def send_state_update(self, state: str):
        """Signal the HUD that the voice pipeline is in a given state."""
        msg = {
            "type": "STATE_CHANGE",
            "id": str(uuid.uuid4()),
            "payload": {"state": state}
        }
        try:
            self._send_queue.put_nowait(json.dumps(msg))
        except Exception as e:
            logger.error(f"Failed to queue state update: {e}")

    def stop(self):
        self.running = False
        if self.ws:
            asyncio.create_task(self.ws.close())

# Singleton
_ipc_client = None

def get_ipc_client():
    global _ipc_client
    if _ipc_client is None:
        _ipc_client = VoiceIPCClient()
    return _ipc_client

def start_ipc_client_sync():
    """Start the IPC client in a new asyncio event loop."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = get_ipc_client()
    try:
        loop.run_until_complete(client.connect_and_listen())
    except KeyboardInterrupt:
        client.stop()
