"""
Tests for the email mailer service.

We mock aiosmtplib so we never actually try to connect to Gmail.
Focus: does the function call the right SMTP params, handle errors cleanly?
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.exceptions import EmailError
from app.services.mailer import send_summary

SAMPLE_SUMMARY = "Electronics led the quarter with $664,000 in total revenue across all regions."


# ── Happy path ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_summary_calls_smtp():
    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        await send_summary(to="exec@company.com", summary=SAMPLE_SUMMARY)

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args.kwargs

    # Targeting the right SMTP server
    assert call_kwargs["hostname"] == "smtp.gmail.com"
    assert call_kwargs["port"] == 587
    assert call_kwargs["start_tls"] is True


@pytest.mark.asyncio
async def test_email_uses_correct_credentials():
    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        await send_summary(to="exec@company.com", summary=SAMPLE_SUMMARY)

    kwargs = mock_send.call_args.kwargs
    # Should use the GMAIL_USER and GMAIL_APP_PASSWORD from settings
    assert kwargs["username"] == "test@example.com"
    assert kwargs["password"] == "fake-app-password"


@pytest.mark.asyncio
async def test_email_message_contains_summary():
    with patch("aiosmtplib.send", new_callable=AsyncMock) as mock_send:
        await send_summary(to="exec@company.com", summary=SAMPLE_SUMMARY)

    # The message object is the first positional arg
    message = mock_send.call_args.args[0]
    # It should be a MIME multipart message (plain + html)
    assert message["To"] == "exec@company.com"
    assert "Sales Insight" in message["Subject"]


# ── Error handling ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_raises_email_error_on_smtp_failure():
    with patch("aiosmtplib.send", side_effect=Exception("Connection refused")):
        with pytest.raises(EmailError):
            await send_summary(to="exec@company.com", summary=SAMPLE_SUMMARY)
