import logging
from typing import Any

import google.generativeai as genai
from groq import Groq

from app.config import get_settings
from app.exceptions import LLMError

logger = logging.getLogger(__name__)


def _build_prompt(stats: dict[str, Any]) -> str:
    """
    Build a structured prompt that gives the LLM all the numbers it needs
    to write a meaningful executive summary — not just bullet points.
    """
    region_lines = "\n".join(
        f"  - {region}: {rev}" for region, rev in stats["revenue_by_region"].items()
    )

    return f"""You are a senior business analyst writing a quarterly sales report for executive leadership.

Based on the following sales data, write a professional, narrative-style summary in 3–4 paragraphs.
Do NOT use bullet points. Write in flowing prose, as if presenting to a board of directors.
Highlight what's working, what's concerning, and any actionable recommendation.

SALES DATA:
- Period: {stats['date_range']}
- Total Revenue: ${stats['total_revenue']:,.2f}
- Total Units Sold: {stats['total_units']:,}
- Top Performing Region: {stats['top_region']}
- Top Product Category: {stats['top_category']}
- Order Status Breakdown: {stats['status_breakdown']}
- Revenue by Region:
{region_lines}

Write the summary now:"""


def generate_summary(stats: dict[str, Any]) -> str:
    """
    Generate an AI narrative summary from parsed sales stats.
    Tries Gemini first; falls back to Groq if Gemini fails for any reason.
    Raises LLMError if both providers fail.
    """
    settings = get_settings()
    prompt = _build_prompt(stats)

    # --- Primary: Gemini 1.5 Flash ---
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning("Gemini failed (%s), falling back to Groq.", e)

    # --- Fallback: Groq Llama3-8b ---
    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        chat = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800,
        )
        return chat.choices[0].message.content.strip()
    except Exception as e:
        logger.error("Groq also failed: %s", e)
        raise LLMError()
