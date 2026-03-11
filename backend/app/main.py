import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.routers.analyze import limiter, router as analyze_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="Sales Insight Automator",
        description=(
            "Upload a CSV or XLSX sales file and receive an AI-generated executive summary "
            "delivered directly to your inbox. Powered by Gemini and Groq."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # added rate limiter , ive reused the limiter instance from analyze.py so it shares state across the app and works properly
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # --- CORS: only allow requests from the configured frontend URL ---
    # Strip trailing slash to avoid mismatch (e.g. "https://x.vercel.app/" vs "https://x.vercel.app")
    frontend_origin = settings.FRONTEND_URL.rstrip("/")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_origin],
        allow_methods=["POST", "GET"],
        allow_headers=["*"],
    )

# injection no no - security purpose
    app.add_middleware(
        TrustedHostMiddleware,
        # "testserver" is the host FastAPI's TestClient uses — it must be in this list
        allowed_hosts=["localhost", "127.0.0.1", "testserver", "*.onrender.com", "*.vercel.app"],
    )

    # all routes are hereee
    app.include_router(analyze_router)

    @app.get("/health", tags=["Health"], summary="Health check")
    async def health():
        return {"status": "ok"}

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        # Log internally but don't leak stack traces to the client
        logger.error("Unhandled exception: %s", exc, exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again."},
        )

    return app


app = create_app()
