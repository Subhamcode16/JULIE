"""Julie background task scheduler."""

import asyncio
from datetime import datetime
from loguru import logger

# Phase 3: We implement a lightweight async scheduler instead of pulling in APScheduler
# to keep dependencies lean, or we can use APScheduler if needed.
# For now, a simple async loop for scheduled tasks works perfectly.

class Scheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
        self._task = None

    async def start(self):
        if self.running:
            return
        self.running = True
        logger.info("Background scheduler started.")
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Background scheduler stopped.")

    async def _loop(self):
        while self.running:
            now = datetime.now().timestamp()
            pending_tasks = []
            
            for task in self.tasks:
                if now >= task["execute_at"]:
                    try:
                        logger.info(f"Executing scheduled task: {task['description']}")
                        # In the future, this will trigger the agent or send a WebSocket message
                        # await execute_intent(task['action'])
                    except Exception as e:
                        logger.error(f"Scheduled task failed: {e}")
                else:
                    pending_tasks.append(task)
                    
            self.tasks = pending_tasks
            await asyncio.sleep(1)

    def schedule_task(self, delay_seconds: int, description: str, action: dict):
        """Schedule a task to run after a certain delay."""
        execute_at = datetime.now().timestamp() + delay_seconds
        self.tasks.append({
            "execute_at": execute_at,
            "description": description,
            "action": action
        })
        logger.info(f"Task scheduled in {delay_seconds}s: {description}")

# Singleton
_scheduler = None

def get_scheduler() -> Scheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = Scheduler()
    return _scheduler
