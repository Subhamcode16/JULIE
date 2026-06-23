"""Julie core FastAPI application."""

import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

try:
    from brain.groq_client import answer_with_llm, classify_with_llm, parse_classifier_json
    from brain.prompt_builder import build_prompt
    from core.config import get_config
    from core.database import close_db, init_db
    from core.memory import get_recent_turns, get_relevant_memories, save_conversation_turn
    from core.router import ClassifiedIntent, IntentType, classify_intent
    from core.security import SecurityZone, action_name_for_params, classify_zone, describe_zone
    from core.token_tracker import log_token_usage
    from core.tool_executor import execute_intent
    from core.scheduler import get_scheduler
    from core.cache import get_cached_response, set_cached_response
    from core.agent_core import execute_with_verification
    import core.whatsapp_gateway as whatsapp_gateway
except ImportError:
    from julie.brain.groq_client import answer_with_llm, classify_with_llm, parse_classifier_json
    from julie.brain.prompt_builder import build_prompt
    from julie.core.config import get_config
    from julie.core.database import close_db, init_db
    from julie.core.memory import get_recent_turns, get_relevant_memories, save_conversation_turn
    from julie.core.router import ClassifiedIntent, IntentType, classify_intent
    from julie.core.security import SecurityZone, action_name_for_params, classify_zone, describe_zone
    from julie.core.token_tracker import log_token_usage
    from julie.core.tool_executor import execute_intent
    from julie.core.scheduler import get_scheduler
    from julie.core.cache import get_cached_response, set_cached_response
    from julie.core.agent_core import execute_with_verification
    import julie.core.whatsapp_gateway as whatsapp_gateway


app = FastAPI(title="Julie Core", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address, default_limits=["50/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

config = get_config()
db = None
active_connections = []
pending_actions = {}

CONFIRMATION_TIMEOUT_SECONDS = 5


async def broadcast_state(state: str) -> None:
    """Broadcast Julie's current state to all connected WebSocket clients (e.g. the HUD)."""
    msg = {"type": "STATE_CHANGE", "payload": {"state": state}}
    dead = []
    for conn in active_connections:
        try:
            await conn.send_json(msg)
        except Exception:
            dead.append(conn)
    for conn in dead:
        if conn in active_connections:
            active_connections.remove(conn)

async def broadcast_audio(wav_bytes: bytes) -> None:
    """Broadcast raw WAV audio to all connected WebSocket clients."""
    dead = []
    for conn in active_connections:
        try:
            await conn.send_bytes(wav_bytes)
        except Exception:
            dead.append(conn)
    for conn in dead:
        if conn in active_connections:
            active_connections.remove(conn)


fastapi_loop = None

def sync_broadcast_audio(wav_bytes):
    if fastapi_loop and fastapi_loop.is_running():
        import asyncio
        asyncio.run_coroutine_threadsafe(broadcast_audio(wav_bytes), fastapi_loop)

@app.on_event("startup")
async def startup_event():
    """Initialize database and log startup."""
    global db, fastapi_loop
    import asyncio
    fastapi_loop = asyncio.get_running_loop()
    
    import julie.voice.speaker as speaker
    speaker.set_audio_callback(sync_broadcast_audio)
    
    logger.add(
        Path(config.julie_data_dir) / "julie.log",
        rotation="500 MB",
        retention="7 days",
    )

    logger.info("Julie core starting...")
    db = await init_db(config.db_path)
    logger.info(f"Database initialized at {config.db_path}")
    logger.info(f"WebSocket: ws://127.0.0.1:{config.julie_port_ws}")
    logger.info(f"HTTP: http://127.0.0.1:{config.julie_port_http}")
    await get_scheduler().start()
    logger.info("Ready.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup."""
    global db
    if db:
        await close_db(db)
    await get_scheduler().stop()
    logger.info("Julie core shutting down.")


@app.get("/health")
async def health():
    """Health check."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/config")
async def get_app_config():
    """Return current config with sensitive fields omitted."""
    return {
        "wake_word": config.julie_wake_word,
        "voice": config.julie_voice,
        "log_level": config.julie_log_level,
        "ws_port": config.julie_port_ws,
        "http_port": config.julie_port_http,
    }


@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """Webhook verification for Meta Cloud API."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == config.whatsapp_verify_token:
            logger.info("WhatsApp webhook verified successfully.")
            return int(challenge)
        else:
            return {"error": "Verification failed"}
    return {"error": "Missing parameters"}


@app.post("/webhook/whatsapp")
async def receive_whatsapp_webhook(request: Request):
    """Receive messages from WhatsApp."""
    data = await request.json()
    logger.debug(f"WhatsApp webhook received: {data}")

    try:
        if data.get("object") == "whatsapp_business_account":
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    if "messages" in value:
                        for msg in value["messages"]:
                            if msg.get("type") == "text":
                                sender_phone = msg["from"]
                                text = msg["text"]["body"].strip()
                                msg_id = msg["id"]
                                
                                # 1. Security Check: Is number allowed?
                                if not whatsapp_gateway.is_number_allowed(sender_phone):
                                    logger.warning(f"Unauthorized WhatsApp message from {sender_phone}")
                                    continue
                                    
                                # 2. Check for confirmation replies
                                if sender_phone in whatsapp_gateway.whatsapp_pending_actions:
                                    if text.lower() == "confirm":
                                        action_id = whatsapp_gateway.whatsapp_pending_actions.pop(sender_phone)
                                        # Process confirmation
                                        conf_payload = {"action_id": action_id, "decision": "confirm"}
                                        resp = await handle_confirmation(conf_payload)
                                        await whatsapp_gateway.send_whatsapp_message(sender_phone, resp.get("response", "Action confirmed."))
                                        return {"status": "ok"}
                                    elif text.lower() == "cancel":
                                        whatsapp_gateway.whatsapp_pending_actions.pop(sender_phone)
                                        await whatsapp_gateway.send_whatsapp_message(sender_phone, "Action cancelled.")
                                        return {"status": "ok"}
                                
                                # 3. Normal input routing
                                payload = {
                                    "text": text,
                                    "source": "whatsapp",
                                    "session_id": f"whatsapp_{sender_phone}"
                                }
                                
                                # Route it through the core pipeline
                                response = await handle_user_input(payload, msg_id)
                                
                                # 4. Handle YELLOW zones
                                if response.get("needs_confirmation"):
                                    whatsapp_gateway.whatsapp_pending_actions[sender_phone] = response["action_id"]
                                    confirm_msg = f"{response['response']}\n\nReply 'confirm' to execute, or 'cancel' to abort."
                                    await whatsapp_gateway.send_whatsapp_message(sender_phone, confirm_msg)
                                else:
                                    # Normal response
                                    await whatsapp_gateway.send_whatsapp_message(sender_phone, response.get("response", "Done."))
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")

    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for UI, voice, and terminal clients."""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Client connected. Total: {len(active_connections)}")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            msg_type = data.get("type")
            msg_id = data.get("id", str(uuid.uuid4()))
            payload = data.get("payload", {})

            logger.info(f"Received WS Message: {msg_type} | {msg_id}")

            if msg_type in {"USER_INPUT_TEXT", "USER_INPUT_VOICE"}:
                # Apply global rate limit logic to WebSocket manually using limiter
                client_ip = websocket.client.host if websocket.client else "127.0.0.1"
                try:
                    from limits import parse
                    if not limiter.limiter.hit(parse("50/minute"), client_ip):
                        response = {"success": False, "error": "Rate limit exceeded (50/minute). Please try again later."}
                        await websocket.send_json({
                            "type": f"{msg_type}_RESPONSE",
                            "id": msg_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "payload": response,
                        })
                        continue
                except Exception as e:
                    logger.error(f"Rate limit hit error: {e}")

                # Broadcast LISTENING -> THINKING state transitions to the HUD
                if payload.get("source") == "voice":
                    await broadcast_state("THINKING")
                
                response = await handle_user_input(payload, msg_id)
                
                if payload.get("source") == "voice" and response.get("response"):
                    import julie.voice.speaker as speaker
                    speaker.speak(response["response"])
                    
                # After response is ready, broadcast SPEAKING then back to IDLE
                await broadcast_state("SPEAKING")
            elif msg_type == "CONFIRM_ACTION":
                response = await handle_confirmation(payload)
            elif msg_type in {"HEALTH_CHECK", "HEARTBEAT"}:
                response = {"status": "ok"}
            else:
                response = {"success": False, "error": f"Unknown message type: {msg_type}"}

            await websocket.send_json(
                {
                    "type": f"{msg_type}_RESPONSE",
                    "id": msg_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": response,
                }
            )
            # Add a realistic visual delay for the "SPEAKING" animation to play properly
            if msg_type in {"USER_INPUT_TEXT", "USER_INPUT_VOICE"}:
                await asyncio.sleep(3)
                # Return to IDLE after reply is dispatched and animation plays
                await broadcast_state("IDLE")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(active_connections)}")
    except Exception as exc:
        logger.error(f"WebSocket error: {exc}")
        if websocket in active_connections:
            active_connections.remove(websocket)


async def handle_confirmation(payload: dict) -> dict:
    """Confirm or cancel a pending YELLOW action."""
    action_id = payload.get("action_id")
    decision = payload.get("decision")
    if not action_id or action_id not in pending_actions:
        return {"success": False, "error": "Unknown or expired action_id"}

    pending = pending_actions.pop(action_id)
    if decision != "confirm":
        return {"success": True, "response": "Cancelled", "action_id": action_id}

    created_at = datetime.fromisoformat(pending["created_at"])
    age_seconds = (datetime.utcnow() - created_at).total_seconds()
    if age_seconds > CONFIRMATION_TIMEOUT_SECONDS:
        return {"success": False, "response": "Confirmation timed out", "action_id": action_id}

    exec_result = await execute_with_verification(pending["classified"], db=db)
    response_text = format_execution_response(exec_result)
    try:
        await save_conversation_turn(
            db,
            session_id=pending.get("payload", {}).get("session_id", "default"),
            role="julie",
            content=str(response_text),
            intent_type=pending["classified"].intent_type.value,
        )
    except Exception:
        pass
    return {"success": exec_result.get("success", False), "response": response_text, "detail": exec_result}


async def handle_user_input(payload: dict, msg_id: str) -> dict:
    """Handle user input from text or voice."""
    text = payload.get("text", "").strip()
    source = payload.get("source", "unknown")
    session_id = payload.get("session_id", "default")

    if not text:
        return {"success": False, "error": "Empty input"}

    logger.info(f"Input from {source}: {text}")

    classified = await classify_user_input(text)
    logger.info(f"Intent: {classified.intent_type.value} (confidence: {classified.confidence:.2f})")

    try:
        await save_conversation_turn(
            db,
            session_id=session_id,
            role="user",
            content=text,
            intent_type=classified.intent_type.value,
            tokens_used=1 if classified.used_llm else 0,
        )
    except Exception as exc:
        logger.warning(f"Failed to save conversation turn: {exc}")

    if classified.params.get("clarification_question"):
        response_text = classified.params["clarification_question"]
        return {
            "success": True,
            "response": response_text,
            "intent": classified.intent_type.value,
            "confidence": classified.confidence,
            "zone": SecurityZone.GREEN.value,
            "params": classified.params,
        }

    action_name = action_name_for_params(classified.intent_type.value, classified.params)
    zone = classify_zone(action_name)

    logger.info(f"Security zone: {zone.value} | {describe_zone(zone)}")

    if zone == SecurityZone.RED:
        response_text = (
            f"I can't do that. {action_name} touches protected system areas. "
            f"Say 'julie unlock {action_name} for this session' to proceed."
        )
        return {
            "success": False,
            "response": response_text,
            "intent": classified.intent_type.value,
            "zone": zone.value,
        }

    if zone == SecurityZone.YELLOW:
        action_id = str(uuid.uuid4())
        pending_actions[action_id] = {
            "classified": classified,
            "payload": payload,
            "created_at": datetime.utcnow().isoformat(),
        }
        response_text = f"Confirmation required for action: {action_name} {classified.params}"
        try:
            await save_conversation_turn(db, session_id=session_id, role="julie", content=response_text, intent_type=classified.intent_type.value)
        except Exception:
            pass
        return {
            "success": True,
            "needs_confirmation": True,
            "action_id": action_id,
            "response": response_text,
            "zone": zone.value,
            "tool": action_name,
        }

    execution_result = await execute_with_verification(classified, db=db)
    if not execution_result.get("success") and classified.intent_type in {IntentType.INFORMATION, IntentType.CONVERSATION}:
        cached = get_cached_response(text)
        if cached:
            execution_result = {
                "success": True,
                "tool": "cache_hit",
                "detail": {"text": cached}
            }
        else:
            execution_result = await call_full_brain(text, session_id)
            if execution_result.get("success"):
                set_cached_response(text, execution_result["detail"]["text"])

    response_text = format_execution_response(execution_result)

    try:
        await save_conversation_turn(db, session_id=session_id, role="julie", content=response_text, intent_type=classified.intent_type.value)
    except Exception as exc:
        logger.warning(f"Failed to save assistant turn: {exc}")

    try:
        recent_turns = await get_recent_turns(db, session_id=session_id, limit=20)
    except Exception:
        recent_turns = []

    return {
        "success": execution_result.get("success", False),
        "response": response_text,
        "intent": classified.intent_type.value,
        "confidence": classified.confidence,
        "zone": zone.value,
        "params": classified.params,
        "detail": execution_result,
        "recent_turns": recent_turns,
    }


async def classify_user_input(text: str) -> ClassifiedIntent:
    """Run rule-first classification with optional cheap LLM fallback."""
    classified = classify_intent(text)
    if classified.confidence >= 0.8:
        return classified

    llm_result = await classify_with_llm(text)
    if not llm_result.success:
        return classified

    if db:
        await log_token_usage(
            db,
            model=llm_result.model,
            provider=llm_result.provider,
            intent_type="classification",
            tokens_in=llm_result.tokens_in,
            tokens_out=llm_result.tokens_out,
            latency_ms=llm_result.latency_ms,
        )

    parsed = parse_classifier_json(llm_result.content)
    if not parsed:
        return classified

    try:
        intent_type = IntentType(parsed.get("intent", "conversation"))
    except ValueError:
        intent_type = IntentType.CONVERSATION

    if parsed.get("needs_clarification"):
        return ClassifiedIntent(
            intent_type=IntentType.CONVERSATION,
            confidence=float(parsed.get("confidence", 0.5)),
            params={
                "query": text,
                "clarification_question": parsed.get("clarification_question") or "What should I do next?",
            },
            raw_input=text,
            used_llm=True,
        )

    params = parsed.get("extracted_params") if isinstance(parsed.get("extracted_params"), dict) else {}
    if not params:
        params = {"query": text}

    return ClassifiedIntent(
        intent_type=intent_type,
        confidence=float(parsed.get("confidence", 0.6)),
        params=params,
        raw_input=text,
        used_llm=True,
    )


async def call_full_brain(text: str, session_id: str) -> dict:
    """Use the full prompt path for information/conversation turns."""
    if not db:
        return {"success": False, "error": "Database is not initialized"}

    history = await get_recent_turns(db, session_id=session_id, limit=10)
    memories = await get_relevant_memories(db, text, limit=5)
    prompt = build_prompt(text, history, memories)
    llm_result = await answer_with_llm(prompt)

    if not llm_result.success:
        return {"success": False, "tool": "full_brain", "error": f"LLM unavailable: {llm_result.error}"}

    await log_token_usage(
        db,
        model=llm_result.model,
        provider=llm_result.provider,
        intent_type="full_brain",
        tokens_in=llm_result.tokens_in,
        tokens_out=llm_result.tokens_out,
        latency_ms=llm_result.latency_ms,
    )
    return {
        "success": True,
        "tool": "full_brain",
        "detail": {
            "text": llm_result.content,
            "tokens": {
                "provider": llm_result.provider,
                "model": llm_result.model,
                "tokens_in": llm_result.tokens_in,
                "tokens_out": llm_result.tokens_out,
                "latency_ms": llm_result.latency_ms,
            },
        },
    }


def format_execution_response(execution_result: dict) -> str:
    """Convert a tool result into Julie's short response text."""
    if not execution_result.get("success"):
        return execution_result.get("error", "I'm sorry, but that action could not be completed.")

    detail = execution_result.get("detail")
    tool = execution_result.get("tool")

    if tool == "save_memory" and isinstance(detail, dict):
        return f"Got it, I'll remember that {detail.get('value')}."
    if tool == "list_memories" and isinstance(detail, dict):
        memories = detail.get("memories", [])
        if not memories:
            return "I don't have any memories saved right now."
        return f"I have {len(memories)} memories saved."
    if tool == "get_token_summary" and isinstance(detail, dict):
        return (
            f"Token usage today: {detail.get('total_calls', 0)} calls, "
            f"{detail.get('tokens_in', 0)} input tokens, "
            f"{detail.get('tokens_out', 0)} output tokens. "
        )
    if tool in {"full_brain", "cache_hit"} and isinstance(detail, dict):
        return detail.get("text", "")

    # Natural conversational confirmations for system actions
    if tool == "launch_application":
        return "Opening the application for you now."
    if tool == "run_terminal_command":
        return "I've executed the terminal command."
    if tool == "list_directory":
        return "I've scanned the directory."
    if tool == "read_file":
        return "I have read the file contents."
    if tool == "write_file":
        return "I've successfully saved the file."

    return "Action completed."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=config.julie_port_http,
        ws_ping_interval=20,
        ws_ping_timeout=20,
    )
