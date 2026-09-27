import logging

from internship_agent.services.notification.telegram import TelegramNotifier
from internship_agent.state import InternshipSearchState

logger = logging.getLogger(__name__)


async def send_notification_node(state: InternshipSearchState) -> dict[str, bool]:
    """LangGraph node to send daily digest notifications via Telegram."""
    digest = state.get("digest", "")
    sent = False
    if digest:
        notifier = TelegramNotifier()
        sent = await notifier.send_message(digest)
        if sent:
            logger.info("Daily digest successfully delivered to Telegram.")
        else:
            logger.warning("Failed or skipped delivering daily digest to Telegram.")
    return {"notification_sent": sent}
