"""Screen vision tools for Julie using MSS and Groq Vision."""

import io
import base64
import mss
from PIL import Image
from loguru import logger
from typing import Optional, Dict, Any

try:
    from brain.groq_client import answer_with_vision
except ImportError:
    from julie.brain.groq_client import answer_with_vision


def capture_screen_base64() -> str:
    """Capture screen and return base64 encoded jpeg."""
    with mss.mss() as sct:
        # Grab the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # Resize if width > 1280 to save tokens and latency
        if img.width > 1280:
            ratio = 1280.0 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1280, new_height), Image.Resampling.LANCZOS)
            
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


async def analyze_screen(prompt: str) -> Dict[str, Any]:
    """Capture screen and ask Groq Vision a question about it."""
    try:
        b64_image = capture_screen_base64()
        result = await answer_with_vision(prompt, b64_image)
        return {
            "success": result.success,
            "answer": result.content,
            "error": result.error
        }
    except Exception as e:
        logger.error(f"Screen analysis error: {e}")
        return {"success": False, "error": str(e)}
