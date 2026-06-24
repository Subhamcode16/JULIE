"""Tracks the cursor and detects user interruptions."""

import asyncio
import pyautogui
from loguru import logger
import math

class CursorTracker:
    def __init__(self):
        self.is_tracking = False
        self.is_ai_controlled = False
        self.current_x = 0
        self.current_y = 0
        self.last_human_x = 0
        self.last_human_y = 0
        self.broadcast_callback = None
        self._task = None

    def start(self, broadcast_callback):
        self.broadcast_callback = broadcast_callback
        self.is_tracking = True
        self._task = asyncio.create_task(self._tracking_loop())
        logger.info("Cursor tracking started.")

    def stop(self):
        self.is_tracking = False
        if self._task:
            self._task.cancel()
        logger.info("Cursor tracking stopped.")

    def set_ai_controlled(self, controlled: bool):
        """Called by agent_core when taking or releasing control."""
        self.is_ai_controlled = controlled
        if controlled:
            # Snapshot the current human pos so we can detect if they move
            # while AI is active.
            try:
                x, y = pyautogui.position()
                self.last_human_x = x
                self.last_human_y = y
            except Exception:
                pass

    async def _tracking_loop(self):
        """Poll the mouse position at 60fps."""
        while self.is_tracking:
            try:
                # pyautogui.position() is fast, but we can offload if needed.
                # It's usually safe to call in the event loop directly for just polling coords.
                x, y = pyautogui.position()
                
                # Check for interruption
                if self.is_ai_controlled:
                    dist = math.hypot(x - self.last_human_x, y - self.last_human_y)
                    # If human physically moved mouse by more than 50 pixels, interrupt!
                    if dist > 50:
                        logger.warning("Human mouse movement detected! Interrupting AI Cursor!")
                        self.is_ai_controlled = False
                        # We could emit an interrupt event here to agent_core.
                        # For now we just release control visual state.
                else:
                    self.last_human_x = x
                    self.last_human_y = y

                self.current_x = x
                self.current_y = y

                if self.broadcast_callback:
                    await self.broadcast_callback({
                        "type": "cursor_update",
                        "x": self.current_x,
                        "y": self.current_y,
                        "is_active": True,
                        "is_ai_controlled": self.is_ai_controlled
                    })
            except Exception as e:
                pass
                
            await asyncio.sleep(1 / 60) # ~60fps

cursor_tracker = CursorTracker()
