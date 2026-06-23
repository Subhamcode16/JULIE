"""Tools for accessing the Windows Accessibility tree."""

import uiautomation as auto
import pyautogui
from loguru import logger
from typing import Dict, Any, Optional

def get_element_under_cursor() -> Optional[Dict[str, Any]]:
    """
    Uses Windows UIAutomation to read the element directly under the current mouse cursor.
    This is extremely fast and exact, but may fail on custom UI frameworks (like Qt or some games).
    """
    try:
        x, y = pyautogui.position()
        control = auto.ControlFromPoint(x, y)
        if not control:
            return None

        # Gather relevant info
        name = control.Name
        control_type = control.ControlTypeName
        class_name = control.ClassName
        # Some elements have a ValuePattern (like textboxes)
        value = ""
        if hasattr(auto.PatternId, 'ValuePattern'):
            try:
                # Need to check if it supports the pattern, safely
                pattern = control.GetValuePattern()
                if pattern:
                    value = pattern.Value
            except Exception:
                pass
                
        # Bounding rect
        rect = control.BoundingRectangle
        bbox = None
        if rect:
            bbox = {"left": rect.left, "top": rect.top, "right": rect.right, "bottom": rect.bottom}

        return {
            "success": True,
            "x": x,
            "y": y,
            "name": name,
            "control_type": control_type,
            "class_name": class_name,
            "value": value,
            "bbox": bbox
        }
    except Exception as e:
        logger.error(f"Accessibility API failed: {e}")
        return None
