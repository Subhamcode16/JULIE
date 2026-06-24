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
from PIL import ImageDraw
import hashlib
import time

_vision_cache = {}
CACHE_TTL = 300 # 5 minutes


def capture_screen_base64(draw_cursor: bool = False, cx: int = 0, cy: int = 0) -> str:
    """Capture screen and return base64 encoded jpeg with aggressive compression."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        if draw_cursor:
            draw = ImageDraw.Draw(img)
            r = 15
            draw.ellipse((cx-r, cy-r, cx+r, cy+r), outline="red", width=5)

        # Aggressive resize for LLM processing speed
        max_width = 1024
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.NEAREST) # NEAREST is faster
            
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=60, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")


async def analyze_screen(prompt: str, draw_cursor: bool = False, cx: int = 0, cy: int = 0) -> Dict[str, Any]:
    """Capture screen and ask Groq Vision a question about it, with caching."""
    try:
        b64_image = capture_screen_base64(draw_cursor, cx, cy)
        
        # Cache key based on image hash and prompt
        img_hash = hashlib.md5(b64_image.encode()).hexdigest()
        cache_key = f"{img_hash}_{prompt}"
        
        now = time.time()
        if cache_key in _vision_cache:
            entry = _vision_cache[cache_key]
            if now - entry["time"] < CACHE_TTL:
                logger.debug("Vision cache hit!")
                return entry["result"]
                
        result = await answer_with_vision(prompt, b64_image)
        
        final_result = {
            "success": result.success,
            "answer": result.content,
            "error": result.error
        }
        
        if result.success:
            _vision_cache[cache_key] = {"time": now, "result": final_result}
            
        return final_result
    except Exception as e:
        logger.error(f"Screen analysis error: {e}")
        return {"success": False, "error": str(e)}

async def analyze_cursor_context(prompt: str) -> Dict[str, Any]:
    """Capture screen with a red dot at the cursor and analyze it."""
    import pyautogui
    x, y = pyautogui.position()
    return await analyze_screen(prompt, draw_cursor=True, cx=x, cy=y)

async def find_text_on_screen(text: str) -> Dict[str, Any]:
    """Find specific text on the screen using Vision OCR."""
    prompt = f"Find the exact location of the text '{text}' on the screen. Return its approximate bounding box or position."
    return await analyze_screen(prompt)

async def verify_action(expected_state: str) -> bool:
    """Take a screenshot and verify if the expected UI state is present."""
    prompt = f"Does this screenshot show that the following state is achieved: '{expected_state}'? Reply strictly with YES or NO, followed by a brief reason."
    result = await analyze_screen(prompt)
    if result["success"]:
        answer = result["answer"].upper()
        return "YES" in answer[:10]
    return False

