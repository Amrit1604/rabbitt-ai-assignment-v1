import logging

from fastapi import APIRouter, File, Form, Request, UploadFile
from pydantic import EmailStr
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings
from app.exceptions import FileValidationError
from app.schemas import AnalyzeResponse
from app.services import llm, mailer, parser

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

ALLOWED_EXTENSIONS = {".csv", ".xlsx"}


@router.post(
    "/api/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze a sales file and email the AI summary",
    description=(
        "Upload a CSV or XLSX sales data file along with a recipient email address. "
        "The service parses the data, generates an AI-powered narrative summary via Gemini "
        "(with Groq as fallback), and delivers it straight to the inbox."
    ),
    tags=["Analysis"],
)
@limiter.limit("10/minute")
async def analyze(
    request: Request,  # required by slowapi
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

    # --- Parse → Generate → Email ---
    stats = parser.validate_and_parse(file_bytes, file.filename or "upload")
    summary = llm.generate_summary(stats)
    await mailer.send_summary(to=str(email), summary=summary)

    return AnalyzeResponse(
        message=f"Summary generated and sent to {email}.",
        summary=summary,
    )
