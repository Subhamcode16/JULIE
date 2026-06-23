"""Tools for agentic Action-Observation loops and contextual pointing."""

import asyncio
import json
import pyautogui
from typing import Dict, Any
from loguru import logger

try:
    from tools.accessibility_tools import get_element_under_cursor
    from tools.browser_tools import get_browser_context
    from brain.groq_client import answer_with_vision
    from core.cursor_tracker import cursor_tracker
except ImportError:
    from julie.tools.accessibility_tools import get_element_under_cursor
    from julie.tools.browser_tools import get_browser_context
    from julie.brain.groq_client import answer_with_vision
    from julie.core.cursor_tracker import cursor_tracker

async def execute_contextual_action(action_type: str, text: str = "") -> Dict[str, Any]:
    """Execute a contextual action (like 'type in here') using hybrid context."""
    logger.info(f"Executing contextual action: {action_type}")
    
    # Take visual control
    cursor_tracker.set_ai_controlled(True)
    
    try:
        # Hybrid Approach: Try Accessibility API first
        element = get_element_under_cursor()
        
        # We always click to focus where the human is pointing
        x, y = pyautogui.position()
        pyautogui.click(x, y)
        await asyncio.sleep(0.5)

        if action_type == "type":
            # If we know the element, we could theoretically do things with it.
            # But the simplest is just typing directly now that we focused it.
            pyautogui.write(text, interval=0.02)
            return {"success": True, "message": f"Typed '{text}' at the cursor location."}
            
    finally:
        cursor_tracker.set_ai_controlled(False)
        
    return {"success": False, "error": "Contextual action failed or interrupted."}

async def autonomous_browser_loop(goal: str, max_steps: int = 10) -> Dict[str, Any]:
    """Autonomous Action-Observation loop strictly constrained within CloakBrowser."""
    logger.info(f"Starting autonomous browser loop for goal: {goal}")
    
    try:
        context = await get_browser_context()
        page = context.pages[0] if context.pages else await context.new_page()
        
        system_prompt = (
            "You are an autonomous browser agent. You will be given a screenshot of a browser page. "
            "Your goal is: " + goal + ". "
            "You must output STRICTLY JSON in the format: "
            '{"action": "click"|"type"|"goto"|"complete", "target": "css selector or url", "text": "text to type if applicable", "reason": "why"}'
        )

        for step in range(max_steps):
            logger.info(f"Autonomous step {step+1}/{max_steps}")
            # Take screenshot of the browser page (constrained to CloakBrowser)
            screenshot_bytes = await page.screenshot(type="jpeg", quality=60)
            import base64
            b64_image = base64.b64encode(screenshot_bytes).decode("utf-8")
            
            prompt = system_prompt + f"\n\nWhat is your next action to achieve the goal?"
            result = await answer_with_vision(prompt, b64_image)
            
            if not result.success:
                return {"success": False, "error": "Vision LLM failed during autonomous loop."}
                
            try:
                # Naive JSON extraction
                content = result.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].strip()
                    
                action_data = json.loads(content)
                action = action_data.get("action")
                target = action_data.get("target")
                text = action_data.get("text")
                reason = action_data.get("reason", "")
                
                logger.info(f"AI decided to: {action} on {target} because {reason}")
                
                if action == "complete":
                    return {"success": True, "message": "Autonomous goal achieved."}
                elif action == "click" and target:
                    await page.click(target, timeout=5000)
                elif action == "type" and target and text:
                    await page.fill(target, text, timeout=5000)
                elif action == "goto" and target:
                    if not target.startswith("http"):
                        target = "https://" + target
                    await page.goto(target)
                else:
                    logger.warning(f"Unknown action or missing target: {action}")
                
                await asyncio.sleep(2) # Let page load
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON from Vision model: {result.content}")
                
        return {"success": False, "error": "Max steps reached without completing the goal."}
    except Exception as e:
        logger.error(f"Autonomous loop error: {e}")
        return {"success": False, "error": str(e)}
