import io
import logging
from typing import Any

import magic
import pandas as pd

from app.exceptions import FileValidationError

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {
    "text/plain": "csv",
    "application/csv": "csv",
    "text/csv": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "xlsx",
    "application/zip": "xlsx",  #for zips zzz..
}

REQUIRED_COLUMNS = {"Revenue", "Region", "Product_Category", "Units_Sold", "Date", "Status"}


def validate_and_parse(file_bytes: bytes, filename: str) -> dict[str, Any]:
    """
    Validate a file by its magic bytes (not just extension), then parse it
    into a structured stats dictionary for the LLM prompt.

    Raises FileValidationError for any bad input.
    """
    mime = magic.from_buffer(file_bytes[:2048], mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise FileValidationError(
            f"Unsupported file type '{mime}'. Please upload a CSV or XLSX file."
        )

#loading of dataframes from bytes can be tricky because pandas doesn't natively support file-like objects for all formats, and we also want to handle both CSV and XLSX. The magic library helps us identify the MIME type, but we should also have a fallback based on file extension just in case. We'll try to read the file using pandas with the appropriate engine based on the detected type. If it fails, we'll raise a validation error.
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    try:
        if ext == "xlsx" or mime in (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/zip",
        ):
            df = pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
        else:
            df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as e:
        logger.warning("Failed to parse uploaded file: %s", e)
        raise FileValidationError("Could not read the file. Make sure it is a valid CSV or XLSX.")

    # Verify expected columns exist (case-insensitive check)
    df.columns = [c.strip() for c in df.columns]
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise FileValidationError(
            f"Missing required columns: {', '.join(sorted(missing))}. "
            "Expected: Date, Product_Category, Region, Units_Sold, Revenue, Status."
        )

    # Drop rows that have no data at all
    df.dropna(how="all", inplace=True)
    if df.empty:
        raise FileValidationError("The uploaded file contains no data rows.")

    return _extract_stats(df)


def _extract_stats(df: pd.DataFrame) -> dict[str, Any]:
    """Pull the key numbers out of the DataFrame. Returns a plain dict."""
    df["Revenue"] = pd.to_numeric(df["Revenue"], errors="coerce").fillna(0)
    df["Units_Sold"] = pd.to_numeric(df["Units_Sold"], errors="coerce").fillna(0)

    total_revenue = float(df["Revenue"].sum())
    total_units = int(df["Units_Sold"].sum())

    top_region = df.groupby("Region")["Revenue"].sum().idxmax()
    top_category = df.groupby("Product_Category")["Revenue"].sum().idxmax()

    # Date range + monthly trend (best-effort — ignore if column isn't parseable)
    date_range = "Unknown"
    monthly_revenue: dict[str, float] = {}
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        date_range = (
            f"{df['Date'].min().strftime('%B %d, %Y')} – {df['Date'].max().strftime('%B %d, %Y')}"
        )
        df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
        monthly_revenue = (
            df.groupby("YearMonth")["Revenue"].sum().sort_index().to_dict()
        )
    except Exception:
        pass

    status_counts = df["Status"].value_counts().to_dict()
    status_breakdown = ", ".join(f"{k}: {v}" for k, v in status_counts.items())
    cancellation_count = int(status_counts.get("Cancelled", 0))

    # Raw floats — used by chart generator; LLM prompt formats them as strings
    revenue_by_region: dict[str, float] = (
        df.groupby("Region")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    revenue_by_category: dict[str, float] = (
        df.groupby("Product_Category")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    return {
        "total_revenue": total_revenue,
        "total_units": total_units,
        "top_region": top_region,
        "top_category": top_category,
        "date_range": date_range,
        "status_breakdown": status_breakdown,
        "cancellation_count": cancellation_count,
        "revenue_by_region": revenue_by_region,
        "revenue_by_category": revenue_by_category,
        "monthly_revenue": monthly_revenue,
        "row_count": len(df),
    }
