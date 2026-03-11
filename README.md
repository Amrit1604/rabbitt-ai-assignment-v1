# Sales Insight Automator

Upload a CSV or XLSX sales file — get an AI-generated executive summary delivered straight to your inbox. Built with FastAPI, Next.js, Gemini, and Gmail SMTP.

---

## Quick Start (Docker)

### 1. Clone and configure

```bash
git clone https://github.com/YOUR_USERNAME/sales-insight-automator.git
cd sales-insight-automator

cp .env.example .env
# Open .env and fill in your API keys (see section below)
```

### 2. Spin up with docker-compose

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the following:

| Key | Description | Where to get it |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (primary LLM) | https://aistudio.google.com/app/apikey |
| `GROQ_API_KEY` | Groq API key (fallback LLM) | https://console.groq.com/keys |
| `GMAIL_USER` | Your full Gmail address | — |
| `GMAIL_APP_PASSWORD` | Gmail App Password (**not** your login password) | https://myaccount.google.com/apppasswords |
| `FRONTEND_URL` | URL the frontend is served from (CORS) | `http://localhost:3000` for local dev |
| `NEXT_PUBLIC_API_URL` | URL the frontend uses to reach the backend | `http://localhost:8000` for local dev |
| `MAX_FILE_MB` | Max upload size in MB | Default: `5` |

> **Note on Gmail App Password**: You must have 2-Step Verification enabled on your Google account before you can create an App Password.

---

## How It Works

```
User uploads CSV/XLSX + email
        │
        ▼
POST /api/analyze
        │
        ├─ Validate file (magic bytes + size + MIME)
        ├─ Parse with pandas → extract stats
        ├─ Generate narrative via Gemini (Groq fallback)
        └─ Send HTML email via Gmail SMTP
        │
        ▼
Response: { message, summary }
```

---

## Security Overview

| Control | Implementation |
|---|---|
| **Rate limiting** | `slowapi` — 10 requests/min per IP on `/api/analyze` |
| **File validation** | Magic-bytes check (not just file extension) + MIME whitelist + 5 MB cap |
| **CORS** | Restricted to `FRONTEND_URL` only — no wildcard |
| **Host header injection** | `TrustedHostMiddleware` on FastAPI |
| **Input validation** | `pydantic EmailStr` validates recipient server-side |
| **Non-root containers** | Both Dockerfiles create and run as `appuser` |
| **Secret management** | All secrets in `.env`, never hardcoded. `.env.example` ships with empty values. |

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # App factory, middleware, routing
│   │   ├── config.py            # Env vars (pydantic-settings)
│   │   ├── schemas.py           # Response models → Swagger auto-docs
│   │   ├── exceptions.py        # Custom HTTP exceptions
│   │   ├── routers/
│   │   │   └── analyze.py       # POST /api/analyze
│   │   └── services/
│   │       ├── parser.py        # CSV/XLSX parsing
│   │       ├── llm.py           # Gemini + Groq
│   │       └── mailer.py        # Gmail SMTP
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                     # Next.js App Router
│   ├── components/              # UploadForm, StatusCard
│   ├── lib/api.ts               # Typed fetch wrapper
│   ├── types/                   # Shared TypeScript interfaces
│   └── Dockerfile
├── .github/workflows/ci.yml     # CI: lint + build on PRs
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Live URLs

| | URL |
|---|---|
| Frontend | _Add after deploying to Vercel_ |
| Backend API / Swagger | _Add after deploying to Render_ |

---

## Sample Test Data

```csv
Date,Product_Category,Region,Units_Sold,Unit_Price,Revenue,Status
2026-01-05,Electronics,North,150,1200,180000,Shipped
2026-01-12,Home Appliances,South,45,450,20250,Shipped
2026-01-20,Electronics,East,80,1100,88000,Delivered
2026-02-15,Electronics,North,210,1250,262500,Delivered
2026-02-28,Home Appliances,North,60,400,24000,Cancelled
2026-03-10,Electronics,West,95,1150,109250,Shipped
```

Save this as `sales_q1_2026.csv` and use it to test the end-to-end flow.

---

## CI/CD

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every pull request to `main`:

- **Backend job**: `ruff` lint + Docker image build
- **Frontend job**: `eslint` + `tsc --noEmit` + `next build`

Both jobs run in parallel. No merge if either fails.
