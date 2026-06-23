import httpx
from loguru import logger
try:
    from core.config import get_config
except ImportError:
    from julie.core.config import get_config

config = get_config()

# A simple dictionary to track phone_number -> pending_action_id 
# so we can intercept confirmations from WhatsApp.
whatsapp_pending_actions = {}


async def send_whatsapp_message(to_number: str, text: str) -> bool:
    """Send a text message via WhatsApp Cloud API."""
    if not config.whatsapp_token or not config.whatsapp_phone_number_id:
        logger.warning("WhatsApp credentials not configured.")
        return False
        
    url = f"https://graph.facebook.com/v17.0/{config.whatsapp_phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {config.whatsapp_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload, timeout=10.0)
            if resp.status_code in (200, 201):
                logger.info(f"WhatsApp message sent to {to_number}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message. {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        return False


def is_number_allowed(phone_number: str) -> bool:
    """Check if the sender's phone number is in the allowed list."""
    if not config.whatsapp_allowed_numbers:
        return True # If no list is provided, allow all (not recommended, but fallback)
    
    allowed = [num.strip() for num in config.whatsapp_allowed_numbers.split(",") if num.strip()]
    if not allowed:
        return True
        
    # Meta sends phone numbers with country code, e.g. "15551234567"
    for allowed_num in allowed:
        if phone_number == allowed_num or phone_number.endswith(allowed_num):
            return True
            
    return False
