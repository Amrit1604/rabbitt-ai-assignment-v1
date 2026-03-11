import logging

from fastapi import APIRouter, BackgroundTasks, File, Form, Request, UploadFile
from pydantic import EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.exceptions import FileValidationError
from app.schemas import AnalyzeResponse
from app.services import charts as charts_service
from app.services import llm, mailer, parser

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


async def _send_report(
    to: str,
    summary: str,
    stats: dict,
) -> None:
    """Background task: generate charts then send the email with attachments."""
    try:
        generated_charts = charts_service.generate_charts(stats)
        await mailer.send_summary(to=to, summary=summary, charts=generated_charts)
    except Exception as exc:
        logger.error("Background report delivery failed for %s: %s", to, exc)


@router.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze a sales file and email the AI summary",
    description=(
        "Upload a CSV or XLSX sales data file along with a recipient email address. "
        "The service parses the data, generates an AI-powered narrative summary via Gemini "
        "(with Groq as fallback), generates charts, and delivers the full report to the inbox. "
        "The AI summary is returned immediately; email is dispatched in the background."
    ),
    tags=["Analysis"],
)
@limiter.limit("10/minute")
async def analyze(
    request: Request,  # required by slowapi
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Sales data file (.csv or .xlsx, max 5 MB)"),
    email: EmailStr = Form(..., description="Recipient email address for the summary"),
) -> AnalyzeResponse:
    settings = get_settings()

    # --- File extension check (quick pre-check before reading bytes) ---
    suffix = (
        f".{file.filename.rsplit('.', 1)[-1].lower()}" if file.filename and "." in file.filename
        else ""
    )
    if suffix not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            f"File type '{suffix}' is not supported. Upload a .csv or .xlsx file."
        )

    # --- Read file and enforce size limit ---
    file_bytes = await file.read()
    max_bytes = settings.MAX_FILE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise FileValidationError(
            f"File exceeds the {settings.MAX_FILE_MB} MB limit "
            f"({len(file_bytes) / 1024 / 1024:.1f} MB uploaded)."
        )

    logger.info("Processing file: %s (%.1f KB)", file.filename, len(file_bytes) / 1024)

    # --- Parse → AI summary (sync, fast return) → email+charts (background) ---
    stats = parser.validate_and_parse(file_bytes, file.filename or "upload")
    summary = llm.generate_summary(stats)
    background_tasks.add_task(_send_report, str(email), summary, stats)

    return AnalyzeResponse(
        message=f"Summary generated! Your report with charts will be sent to {email} shortly.",
        summary=summary,
    )
