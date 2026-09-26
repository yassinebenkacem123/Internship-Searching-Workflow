from unittest.mock import AsyncMock, patch

import pytest

from internship_agent.services.notification.telegram import TelegramNotifier


@pytest.mark.asyncio
async def test_telegram_skipped_when_credentials_missing() -> None:
    notifier = TelegramNotifier(bot_token="", chat_id="")
    success = await notifier.send_message("Test message")
    assert success is False


@pytest.mark.asyncio
async def test_telegram_sends_payload_correctly() -> None:
    notifier = TelegramNotifier(bot_token="test_token", chat_id="123456")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200
        success = await notifier.send_message("Hello from test")

        assert success is True
        mock_post.assert_called_once()
        _args, kwargs = mock_post.call_args
        assert "123456" in str(kwargs.get("json", {}))
        assert "Hello from test" in str(kwargs.get("json", {}))
