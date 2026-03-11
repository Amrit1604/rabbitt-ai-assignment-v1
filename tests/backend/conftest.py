"""
Shared fixtures for all backend tests.

This file is auto-loaded by pytest before any test runs.
It handles the annoying bits — path setup, fake env vars, test client,
and sample file bytes — so individual test files stay clean.
"""

import io
import os
import sys

import pytest

# Make sure Python can find `app/` from the backend folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backend"))

# Fake env vars — must be set before the app module is imported,
# because pydantic-settings & lru_cache lock values at first import.
os.environ.update(
    {
        "GEMINI_API_KEY": "test-gemini-key",
        "GROQ_API_KEY": "test-groq-key",
        "GMAIL_USER": "test@example.com",
        "GMAIL_APP_PASSWORD": "fake-app-password",
        "FRONTEND_URL": "http://localhost:3000",
        "MAX_FILE_MB": "5",
    }
)

from fastapi.testclient import TestClient  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.main import app  # noqa: E402

# Reset the cache so it picks up the fake values above
get_settings.cache_clear()


# ── Reusable CSV content (same as the reference data in todo.md) ─────────────

SAMPLE_CSV_BYTES = b"""Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
2026-01-20,Electronics,East,80,1100,88000,Delivered
2026-02-15,Electronics,North,210,1250,262500,Delivered
2026-02-28,Home Appliances,North,60,400,24000,Cancelled
2026-03-10,Electronics,West,95,1150,109250,Shipped
"""

# What the parser should extract from the CSV above
EXPECTED_STATS = {
    "total_revenue": 664000.0,
    "total_units": 640,
    "top_region": "North",
    "top_category": "Electronics",
    "row_count": 6,
}


@pytest.fixture(scope="session")
def client():
    """In-process test client — no real HTTP, fast as a unit test."""
    return TestClient(app)


@pytest.fixture
def sample_csv():
    """The reference Q1 2026 sales data as raw CSV bytes."""
    return SAMPLE_CSV_BYTES


@pytest.fixture
def sample_xlsx():
    """Same data but in XLSX format, built in-memory with openpyxl."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Date", "Product_Category", "Region", "Units_Sold", "Unit_Price", "Revenue", "Status"])
    ws.append(["2026-01-05", "Electronics", "North", 150, 1200, 180000, "Shipped"])
    ws.append(["2026-01-12", "Home Appliances", "South", 45, 450, 20250, "Shipped"])
    ws.append(["2026-01-20", "Electronics", "East", 80, 1100, 88000, "Delivered"])

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()
