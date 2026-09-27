from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from internship_agent.services.notification.telegram import (
    TelegramNotifier,
    split_message,
)


@pytest.mark.asyncio
async def test_telegram_skipped_when_credentials_missing() -> None:
    notifier = TelegramNotifier(bot_token="", chat_id="")
    success = await notifier.send_message("Test message")
    assert success is False


@pytest.mark.asyncio
async def test_telegram_sends_payload_correctly() -> None:
    notifier = TelegramNotifier(bot_token="test_token", chat_id="123456")

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        success = await notifier.send_message("Hello from test")

        assert success is True
        mock_post.assert_called_once()
        _args, kwargs = mock_post.call_args
        assert "123456" in str(kwargs.get("json", {}))
        assert "Hello from test" in str(kwargs.get("json", {}))


def test_split_message_chunks_properly() -> None:
    # Message shorter than max
    short = "Hello World"
    assert split_message(short, max_chunk_size=100) == [short]

    # Message longer than max
    para1 = "A" * 60
    para2 = "B" * 60
    long_msg = f"{para1}\n\n{para2}"
    chunks = split_message(long_msg, max_chunk_size=70)
    assert len(chunks) == 2
    assert chunks[0] == para1
    assert chunks[1] == para2


@pytest.mark.asyncio
async def test_telegram_chunks_long_message() -> None:
    notifier = TelegramNotifier(bot_token="test_token", chat_id="123456")

    long_text = "\n\n".join([f"Job Opportunity {i}: " + ("x" * 300) for i in range(20)])
    assert len(long_text) > 4000

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        success = await notifier.send_message(long_text)

        assert success is True
        assert mock_post.call_count >= 2
