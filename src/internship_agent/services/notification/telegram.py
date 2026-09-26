import logging

import httpx

from internship_agent.config import get_settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Telegram notification transport for sending daily internship digests."""

    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        settings = get_settings()
        self.bot_token = settings.telegram_bot_token if bot_token is None else bot_token
        self.chat_id = settings.telegram_chat_id if chat_id is None else chat_id

    async def send_message(self, text: str) -> bool:
        """Send a message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id:
            logger.info("Telegram credentials not configured. Skipping Telegram notification.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    logger.info("Telegram notification sent successfully.")
                    return True
                logger.error("Failed to send Telegram message (%d): %s", resp.status_code, resp.text)
        except (httpx.HTTPError, TimeoutError) as exc:
            logger.error("Error communicating with Telegram Bot API: %s", exc)

        return False
