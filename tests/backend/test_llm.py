"""
Tests for the LLM service.

We never call the real Gemini or Groq APIs in tests — that wastes money
and makes tests slow. Instead we mock both clients and verify the
fallback logic works the way it should.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import LLMError
from app.services.llm import generate_summary

SAMPLE_STATS = {
    "total_revenue": 664000.0,
    "total_units": 640,
    "top_region": "North",
    "top_category": "Electronics",
    "date_range": "January 05, 2026 – March 10, 2026",
    "status_breakdown": "Shipped: 3, Delivered: 2, Cancelled: 1",
    "revenue_by_region": {"North": "$466,500", "West": "$109,250", "East": "$88,000", "South": "$20,250"},
    "row_count": 6,
}


# ── Gemini path ───────────────────────────────────────────────────────────────

def test_returns_gemini_summary_when_available():
    mock_response = MagicMock()
    mock_response.text = "  Electronics dominated the quarter with strong North region performance.  "

    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = generate_summary(SAMPLE_STATS)

    # Should strip the whitespace
    assert result == "Electronics dominated the quarter with strong North region performance."


def test_gemini_result_is_a_non_empty_string():
    mock_response = MagicMock()
    mock_response.text = "Some summary text."

    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel") as mock_model_cls:
        mock_model_cls.return_value.generate_content.return_value = mock_response

        result = generate_summary(SAMPLE_STATS)

    assert isinstance(result, str)
    assert len(result) > 0


# ── Fallback to Groq ──────────────────────────────────────────────────────────

def test_falls_back_to_groq_when_gemini_throws():
    groq_text = "Groq generated this fallback summary for the sales team."

    mock_choice = MagicMock()
    mock_choice.message.content = groq_text

    mock_groq_response = MagicMock()
    mock_groq_response.choices = [mock_choice]

    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel", side_effect=Exception("Gemini quota exceeded")), \
         patch("groq.Groq") as mock_groq_cls:
        mock_groq_cls.return_value.chat.completions.create.return_value = mock_groq_response

        result = generate_summary(SAMPLE_STATS)

    assert result == groq_text


# ── Both fail ─────────────────────────────────────────────────────────────────

def test_raises_llm_error_when_both_providers_fail():
    with patch("google.generativeai.configure"), \
         patch("google.generativeai.GenerativeModel", side_effect=Exception("Gemini down")), \
         patch("groq.Groq", side_effect=Exception("Groq also down")):

        with pytest.raises(LLMError):
            generate_summary(SAMPLE_STATS)
