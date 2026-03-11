# Tests

## Structure

```
tests/
├── backend/
│   ├── conftest.py          ← shared fixtures (test client, sample files)
│   ├── pytest.ini           ← pytest config
│   ├── test_parser.py       ← unit tests: file parsing + validation
│   ├── test_llm.py          ← unit tests: Gemini → Groq fallback logic
│   ├── test_mailer.py       ← unit tests: Gmail SMTP async send
│   └── test_analyze_api.py  ← integration tests: full API endpoint + Swagger
└── stress/
    └── locustfile.py        ← load & spike testing with Locust
```

---

## Setup

```bash
cd tests
pip install -r requirements.txt

# The backend app also needs to be importable
pip install -r ../backend/requirements.txt
```

---

## Run the unit + integration tests

```bash
cd tests/backend
pytest -v
```

Run a specific file:
```bash
pytest test_parser.py -v
pytest test_analyze_api.py -v
```

Expected output — all green:
```
tests/backend/test_health.py::test_health_endpoint_is_alive         PASSED
tests/backend/test_parser.py::test_parses_valid_csv                  PASSED
tests/backend/test_parser.py::test_parses_valid_xlsx                 PASSED
...
tests/backend/test_analyze_api.py::test_swagger_ui_is_accessible    PASSED
```

---

## Run the stress test

The backend must be running first:
```bash
# In a separate terminal
cd backend
uvicorn app.main:app --port 8000
```

Then:
```bash
cd tests/stress

# Browser UI at http://localhost:8089
locust -f locustfile.py --host http://localhost:8000

# Headless — 20 users, spawning 5/sec, run for 60 seconds, save HTML report
locust -f locustfile.py --host http://localhost:8000 \
       --headless -u 20 -r 5 --run-time 60s --html report.html
```

### Spike test (rate limiter validation)

```bash
locust -f locustfile.py --host http://localhost:8000 \
       --headless -u 5 -r 5 --run-time 30s --class-picker
# Select SpikeTester class — should see 429s after 10 requests/min per IP
```

---

## What's tested

| Area | Tests |
|---|---|
| File parsing | Valid CSV, valid XLSX, missing columns, empty file, wrong file type |
| LLM service | Gemini success, Groq fallback, both fail → LLMError |
| Mailer service | SMTP called with right params, credentials used, error → EmailError |
| API endpoint | 200 success, 422 bad file/email, 502 on downstream failure |
| Swagger | /docs accessible, /api/analyze documented in OpenAPI schema |
| Rate limiting | 429 expected on spike (validated in stress test) |
