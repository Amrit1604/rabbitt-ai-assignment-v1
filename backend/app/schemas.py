from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    """Response returned after successful file analysis and email dispatch."""

    message: str
    summary: str


class ErrorDetail(BaseModel):
    """Standard error shape used across all exception handlers."""

    detail: str
