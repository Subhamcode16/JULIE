"""Agent handoff to specialized tools like Antigravity CLI."""

import os
import subprocess
from typing import Dict, Any
from loguru import logger

def handoff_to_antigravity(task: str, project_path: str = ".") -> Dict[str, Any]:
    """Package context and hand off the task to Antigravity CLI."""
    logger.info(f"Handing off task to Antigravity CLI: {task}")
    try:
        abs_path = os.path.abspath(project_path)
        
        # Invoke the CLI using a subprocess in a new console
        cmd = ["antigravity", "--task", task, "--dir", abs_path]
        
        CREATE_NEW_CONSOLE = 0x00000010
        process = subprocess.Popen(
            cmd,
            creationflags=CREATE_NEW_CONSOLE,
            cwd=abs_path
        )
        
        return {
            "success": True,
            "message": f"Successfully handed off to Antigravity CLI (PID: {process.pid}). Task: {task}"
        }
    except FileNotFoundError:
        return {"success": False, "error": "Antigravity CLI not found in PATH."}
    except Exception as e:
        logger.error(f"Failed to hand off to Antigravity: {e}")
        return {"success": False, "error": str(e)}
