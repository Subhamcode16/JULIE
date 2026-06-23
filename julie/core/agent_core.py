"""Agent Execution Core with Plan -> Execute -> Verify loop."""

import asyncio
from typing import Dict, Any, List
from loguru import logger
from core.router import ClassifiedIntent
from core.tool_executor import execute_intent
from tools.screen_tools import verify_action

async def execute_with_verification(intent: ClassifiedIntent, db=None) -> Dict[str, Any]:
    """
    Executes an action and then uses vision to verify it succeeded.
    Intent -> Plan -> Execute -> Verify.
    """
    logger.info(f"Agent Core: Planning execution for {intent.intent_type.value}")
    
    # 1. Plan (In a more advanced setup, this would query an LLM for step-by-step)
    # Here we just map the intent directly to the tool executor.
    
    # 2. Execute
    logger.info("Agent Core: Executing...")
    execution_result = await execute_intent(intent, db=db)
    
    if not execution_result.get("success"):
        return execution_result
        
    # 3. Verify
    # We only verify browser or UI actions
    if intent.intent_type.value in ["browser_action", "system_action"]:
        logger.info("Agent Core: Verifying execution via Screen Vision...")
        action_desc = f"Action: {intent.intent_type.value} with params {intent.params}"
        
        # Wait a moment for UI to settle
        await asyncio.sleep(2.0)
        
        verified = await verify_action(action_desc)
        if not verified:
            logger.warning("Agent Core: Verification failed. Action may not have completed successfully.")
            execution_result["verified"] = False
            execution_result["error"] = "Execution seemed to succeed, but vision verification failed."
            execution_result["success"] = False # Revert success if we couldn't verify
        else:
            logger.info("Agent Core: Verification succeeded!")
            execution_result["verified"] = True
            
    return execution_result
