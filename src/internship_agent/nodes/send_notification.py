from internship_agent.services.notification.telegram import TelegramNotifier
from internship_agent.state import InternshipSearchState


async def send_notification_node(state: InternshipSearchState) -> dict[str, None]:
    """LangGraph node to send daily digest notifications via Telegram."""
    digest = state.get("digest", "")
    if digest:
        notifier = TelegramNotifier()
        await notifier.send_message(digest)
    return {}
