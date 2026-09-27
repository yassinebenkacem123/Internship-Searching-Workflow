import logging

import httpx

from internship_agent.config import get_settings

logger = logging.getLogger(__name__)


def split_message(text: str, max_chunk_size: int = 4000) -> list[str]:
    """Split a long text into chunks <= max_chunk_size respecting paragraph or line boundaries."""
    if len(text) <= max_chunk_size:
        return [text]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    # Split by double newline (job boundary) first
    paragraphs = text.split("\n\n")
    for para in paragraphs:
        para_len = len(para) + 2
        if current_length + para_len > max_chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk).strip())
            current_chunk = [para]
            current_length = len(para)
        else:
            current_chunk.append(para)
            current_length += para_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk).strip())

    return chunks


class TelegramNotifier:
    """Telegram notification transport for sending daily internship digests."""

    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        settings = get_settings()
        self.bot_token = settings.telegram_bot_token if bot_token is None else bot_token
        self.chat_id = settings.telegram_chat_id if chat_id is None else chat_id

    async def send_message(self, text: str) -> bool:
        """Send a message to the configured Telegram chat, chunking if exceeding 4000 chars."""
        if not self.bot_token or not self.chat_id:
            logger.info("Telegram credentials not configured. Skipping Telegram notification.")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        chunks = split_message(text, max_chunk_size=4000)
        total_chunks = len(chunks)
        overall_success = True

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                for idx, chunk in enumerate(chunks, 1):
                    message_text = chunk
                    if total_chunks > 1:
                        message_text = f"📨 [Part {idx}/{total_chunks}]\n\n{chunk}"

                    payload = {
                        "chat_id": self.chat_id,
                        "text": message_text,
                        "disable_web_page_preview": True,
                    }
                    resp = await client.post(url, json=payload)
                    if resp.status_code == 200:
                        logger.info("Telegram notification chunk %d/%d sent successfully.", idx, total_chunks)
                    else:
                        logger.error(
                            "Failed to send Telegram message chunk %d/%d (%d): %s",
                            idx,
                            total_chunks,
                            resp.status_code,
                            resp.text,
                        )
                        overall_success = False
        except (httpx.HTTPError, TimeoutError) as exc:
            logger.error("Error communicating with Telegram Bot API: %s", exc)
            return False

        return overall_success
