import httpx
import logging

logger = logging.getLogger(__name__)

async def dispatch_webhook(url: str, payload: dict):
    """Asynchronously sends the parsed EDI JSON payload to a target webhook URL."""
    if not url:
        return

    try:
        # We use a 10-second timeout to prevent zombie connections if the target server is hanging
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()
            logger.info(f"Successfully dispatched webhook to {url}. Status: {response.status_code}")
    except httpx.HTTPStatusError as e:
        logger.error(f"Webhook failed with status {e.response.status_code} for URL: {url}")
    except Exception as e:
        logger.error(f"Failed to dispatch webhook to {url}: {str(e)}")