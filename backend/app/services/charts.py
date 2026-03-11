"""
Chart generation service.

Produces three PNG charts from parsed sales stats:
  1. Revenue by region (bar)
  2. Revenue by product category (bar)
  3. Monthly revenue trend (line)

All charts use the Agg backend — no display required.
"""

import io
import logging
from typing import Any

import matplotlib

matplotlib.use("Agg")  # must be set before any other matplotlib import
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

logger = logging.getLogger(__name__)

_ACCENT = "#0052FF"
_PALETTE = ["#0052FF", "#4D7CFF", "#7B9FFF", "#A8BFFF", "#D0DFFF", "#EBF0FF"]


def generate_charts(stats: dict[str, Any]) -> dict[str, bytes]:
    """
    Generate all charts from a stats dict.
    Returns a mapping of filename → PNG bytes.
    Any chart that fails is skipped silently so a single bad dataset
    doesn't prevent the email from being sent.
    """
    charts: dict[str, bytes] = {}

    for name, fn in [
        ("revenue_by_region.png", _revenue_by_region),
        ("revenue_by_category.png", _revenue_by_category),
        ("monthly_trend.png", _monthly_trend),
    ]:
        try:
            charts[name] = fn(stats)
        except Exception as exc:
            logger.warning("Chart '%s' skipped: %s", name, exc)

    return charts


# ── Individual chart builders ─────────────────────────────────────────────────

def _revenue_by_region(stats: dict[str, Any]) -> bytes:
    data: dict[str, float] = stats["revenue_by_region"]
    if not data:
        raise ValueError("revenue_by_region is empty")

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = (_PALETTE * 10)[: len(data)]
    ax.bar(list(data.keys()), list(data.values()), color=colors, width=0.5)
    ax.set_title("Revenue by Region", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return _to_bytes(fig)


def _revenue_by_category(stats: dict[str, Any]) -> bytes:
    data: dict[str, float] = stats.get("revenue_by_category", {})
    if not data:
        raise ValueError("revenue_by_category is empty")

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = (_PALETTE * 10)[: len(data)]
    ax.bar(list(data.keys()), list(data.values()), color=colors, width=0.5)
    ax.set_title("Revenue by Product Category", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    plt.xticks(rotation=15, ha="right", fontsize=9)
    plt.tight_layout()
    return _to_bytes(fig)


def _monthly_trend(stats: dict[str, Any]) -> bytes:
    monthly: dict[str, float] = stats.get("monthly_revenue", {})
    if not monthly:
        raise ValueError("monthly_revenue is empty")

    months = list(monthly.keys())
    values = list(monthly.values())
    x_pos = list(range(len(months)))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x_pos, values, marker="o", color=_ACCENT, linewidth=2.5, markersize=7)
    ax.fill_between(x_pos, values, alpha=0.08, color=_ACCENT)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(months, rotation=20, ha="right", fontsize=9)
    ax.set_title("Monthly Revenue Trend", fontsize=13, fontweight="bold", pad=10)
    ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.spines[["top", "right"]].set_visible(False)
    plt.tight_layout()
    return _to_bytes(fig)


# ── Helper ────────────────────────────────────────────────────────────────────

def _to_bytes(fig: plt.Figure) -> bytes:
    """Render a matplotlib figure to PNG bytes and close it."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()
