"""
Tests for the file parser service.

Covers: valid CSV, valid XLSX, missing columns, empty file,
bad file type (magic bytes check), and the stats it extracts.
"""

import pytest

from app.exceptions import FileValidationError
from app.services.parser import validate_and_parse

from conftest import EXPECTED_STATS, SAMPLE_CSV_BYTES


# ── Happy path ────────────────────────────────────────────────────────────────

def test_parses_valid_csv(sample_csv):
    stats = validate_and_parse(sample_csv, "sales.csv")

    assert stats["total_revenue"] == EXPECTED_STATS["total_revenue"]
    assert stats["total_units"] == EXPECTED_STATS["total_units"]
    assert stats["top_region"] == EXPECTED_STATS["top_region"]
    assert stats["top_category"] == EXPECTED_STATS["top_category"]
    assert stats["row_count"] == EXPECTED_STATS["row_count"]
    # Status breakdown should list all three statuses
    assert "Shipped" in stats["status_breakdown"]
    assert "Delivered" in stats["status_breakdown"]
    assert "Cancelled" in stats["status_breakdown"]


def test_parses_valid_xlsx(sample_xlsx):
    stats = validate_and_parse(sample_xlsx, "sales.xlsx")

    # 3 data rows in the fixture
    assert stats["row_count"] == 3
    assert stats["top_category"] == "Electronics"
    assert stats["total_revenue"] > 0


def test_date_range_is_human_readable(sample_csv):
    stats = validate_and_parse(sample_csv, "sales.csv")

    # Should look like "January 05, 2026 – March 10, 2026", not a raw timestamp
    assert "2026" in stats["date_range"]
    assert "–" in stats["date_range"]


def test_revenue_by_region_is_formatted(sample_csv):
    stats = validate_and_parse(sample_csv, "sales.csv")

    # Values should be dollar-formatted strings, not raw numbers
    for value in stats["revenue_by_region"].values():
        assert value.startswith("$"), f"Expected '$...' but got: {value}"


# ── Validation errors ─────────────────────────────────────────────────────────

def test_rejects_pdf_bytes():
    # Real PDF magic bytes start with %PDF
    fake_pdf = b"%PDF-1.4 fake pdf content here"
    with pytest.raises(FileValidationError, match="Unsupported file type"):
        validate_and_parse(fake_pdf, "report.pdf")


def test_rejects_missing_required_columns():
    # Valid CSV structure but missing all the columns we need
    bad_csv = b"Name,Age,City\nAlice,30,NYC\n"
    with pytest.raises(FileValidationError, match="Missing required columns"):
        validate_and_parse(bad_csv, "wrong_format.csv")


def test_rejects_empty_csv():
    # Has headers but no data rows
    headers_only = b"Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status\n"
    with pytest.raises(FileValidationError, match="no data rows"):
        validate_and_parse(headers_only, "empty.csv")


def test_rejects_completely_empty_file():
    with pytest.raises(FileValidationError):
        validate_and_parse(b"", "blank.csv")
