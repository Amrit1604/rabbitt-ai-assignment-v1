from fastapi import HTTPException, status


class FileValidationError(HTTPException):
    """Raised when the uploaded file fails type or size checks."""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class LLMError(HTTPException):
    """Raised when both Gemini and Groq fail to generate a summary."""

    def __init__(self, detail: str = "AI summary generation failed. Please try again."):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)


class EmailError(HTTPException):
    """Raised when the email delivery fails."""

    def __init__(self, detail: str = "Summary generated but email delivery failed."):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)
