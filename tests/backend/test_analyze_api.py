"""
Integration tests for POST /api/analyze.

These test the full request/response cycle through FastAPI — routing,
validation, error handling — with LLM and email mocked out so we're
not burning API credits every time someone runs the test suite.
"""

from unittest.mock import AsyncMock, patch

import pytest


# ── Helpers ───────────────────────────────────────────────────────────────────

def _post_file(client, file_bytes, filename, email, content_type="text/plain"):
    """Convenience wrapper so tests stay readable."""
    return client.post(
        "/api/analyze",
        files={"file": (filename, file_bytes, content_type)},
        data={"email": email},
    )


# Mock both external services so nothing hits the real internet
MOCK_SUMMARY = "North region Electronics drove a record $664,000 in Q1 2026 revenue."


def _mocked_services():
    """Return a context manager that patches both LLM and mailer."""
    return (
        patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY),
        patch("app.services.mailer.send_summary", new_callable=AsyncMock),
    )


# ── Health check (sanity) ─────────────────────────────────────────────────────

def test_health_endpoint_is_alive(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Success cases ─────────────────────────────────────────────────────────────

def test_analyze_csv_returns_200(client, sample_csv):
    with patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY), \
         patch("app.services.mailer.send_summary", new_callable=AsyncMock):
        response = _post_file(client, sample_csv, "sales.csv", "boss@company.com")

    assert response.status_code == 200
    body = response.json()
    assert body["summary"] == MOCK_SUMMARY
    assert "boss@company.com" in body["message"]


def test_analyze_xlsx_returns_200(client, sample_xlsx):
    with patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY), \
         patch("app.services.mailer.send_summary", new_callable=AsyncMock):
        response = _post_file(
            client,
            sample_xlsx,
            "sales.xlsx",
            "cfo@company.com",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    assert response.status_code == 200


def test_response_shape_has_message_and_summary(client, sample_csv):
    with patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY), \
         patch("app.services.mailer.send_summary", new_callable=AsyncMock):
        response = _post_file(client, sample_csv, "sales.csv", "team@company.com")

    body = response.json()
    assert "message" in body
    assert "summary" in body


# ── File validation errors ────────────────────────────────────────────────────

def test_rejects_pdf_extension(client):
    fake_pdf = b"%PDF-1.4 not a real spreadsheet"
    response = _post_file(client, fake_pdf, "invoice.pdf", "someone@company.com", "application/pdf")

    assert response.status_code == 422
    assert "not supported" in response.json()["detail"].lower()


def test_rejects_file_exceeding_size_limit(client):
    # 6 MB of 'X' bytes — over the 5 MB limit set in conftest
    big_file = b"Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status\n" + b"X," * (6 * 1024 * 1024)
    response = _post_file(client, big_file, "huge.csv", "someone@company.com")

    assert response.status_code == 422
    assert "limit" in response.json()["detail"].lower()


def test_rejects_missing_columns_in_csv(client):
    bad_csv = b"name,score\nAlice,90\nBob,85\n"
    with patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY), \
         patch("app.services.mailer.send_summary", new_callable=AsyncMock):
        response = _post_file(client, bad_csv, "wrong.csv", "someone@company.com")

    assert response.status_code == 422
    assert "columns" in response.json()["detail"].lower()


# ── Input validation errors ───────────────────────────────────────────────────

def test_rejects_invalid_email(client, sample_csv):
    response = _post_file(client, sample_csv, "sales.csv", "not-an-email")
    # FastAPI/pydantic will reject this before it even hits our handler
    assert response.status_code == 422


def test_rejects_missing_file(client):
    response = client.post("/api/analyze", data={"email": "someone@company.com"})
    assert response.status_code == 422


def test_rejects_missing_email(client, sample_csv):
    response = client.post(
        "/api/analyze",
        files={"file": ("sales.csv", sample_csv, "text/plain")},
    )
    assert response.status_code == 422


# ── Downstream failures ───────────────────────────────────────────────────────

def test_returns_502_when_llm_fails(client, sample_csv):
    from app.exceptions import LLMError

    with patch("app.services.llm.generate_summary", side_effect=LLMError()):
        response = _post_file(client, sample_csv, "sales.csv", "cto@company.com")

    assert response.status_code == 502


def test_returns_502_when_email_fails(client, sample_csv):
    from app.exceptions import EmailError

    with patch("app.services.llm.generate_summary", return_value=MOCK_SUMMARY), \
         patch("app.services.mailer.send_summary", side_effect=EmailError()):
        response = _post_file(client, sample_csv, "sales.csv", "cto@company.com")

    assert response.status_code == 502


# ── Swagger docs ──────────────────────────────────────────────────────────────

def test_swagger_ui_is_accessible(client):
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger" in response.text.lower()


def test_openapi_schema_documents_analyze_endpoint(client):
    schema = client.get("/openapi.json").json()
    assert "/api/analyze" in schema["paths"]
    # Check our Swagger description made it in
    assert "Analysis" in str(schema)
