import logging
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
import base64

from app.config import get_settings
from app.exceptions import EmailError

logger = logging.getLogger(__name__)

GMAIL_SMTP_HOST = "smtp.gmail.com"
GMAIL_SMTP_PORT = 465


def _build_html(summary: str) -> str:
    """
    Convert the markdown-ish summary into a clean HTML email.
    Keeps it simple — no heavy template engine needed for this.
    """
    # Turn newlines into <br> tags so the paragraph breaks survive in email clients
    body = summary.replace("\n\n", "</p><p>").replace("\n", "<br>")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 620px; margin: 40px auto; background: #fff;
                border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,.1); }}
    .header {{ background: #1a1a2e; color: #fff; padding: 28px 32px; }}
    .header h1 {{ margin: 0; font-size: 22px; letter-spacing: .5px; }}
    .header p {{ margin: 4px 0 0; font-size: 13px; opacity: .75; }}
    .body {{ padding: 32px; color: #333; line-height: 1.7; font-size: 15px; }}
    .body p {{ margin-top: 0; }}
    .footer {{ padding: 20px 32px; font-size: 12px; color: #999;
               border-top: 1px solid #eee; text-align: center; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <h1>Sales Insight Report</h1>
      <p>AI-generated summary — Rabbitt AI</p>
    </div>
    <div class="body">
      <p>{body}</p>
    </div>
    <div class="footer">
      This report was generated automatically. Do not reply to this email.
    </div>
  </div>
</body>
</html>"""


async def send_summary(
    to: str,
    summary: str,
    charts: dict[str, bytes] | None = None,
) -> None:
    """
    Send the AI-generated summary as an HTML email via Gmail SMTP (STARTTLS).
    Attaches PNG charts when provided.
    Raises EmailError on any delivery failure so the caller can surface it cleanly.
    """
    settings = get_settings()

    message = MIMEMultipart("mixed")
    message["Subject"] = "Your Sales Insight Report — Rabbitt AI"
    message["From"] = f"Rabbitt AI <{settings.GMAIL_USER}>"
    message["To"] = to

    # Plain-text fallback + HTML body
    alt_part = MIMEMultipart("alternative")
    alt_part.attach(MIMEText(summary, "plain"))
    alt_part.attach(MIMEText(_build_html(summary), "html"))
    message.attach(alt_part)

    # Attach charts as PNG files
    if charts:
        for filename, chart_bytes in charts.items():
            img = MIMEImage(chart_bytes, name=filename)
            img.add_header("Content-Disposition", "attachment", filename=filename)
            message.attach(img)

    try:
        await aiosmtplib.send(
            message,
            hostname=GMAIL_SMTP_HOST,
            port=GMAIL_SMTP_PORT,
            username=settings.GMAIL_USER,
            password=settings.GMAIL_APP_PASSWORD,
            use_tls=True,
        )
        logger.info("Email dispatched to %s", to)
    except Exception as e:
        logger.error("Email delivery failed: %s", e)
        # Fallback to SendGrid
        sg_api_key = getattr(settings, "SENDGRID_API_KEY", None)
        if not sg_api_key:
            logger.error("SendGrid API key not found in settings. Cannot fallback.")
            raise EmailError()

        sg = sendgrid.SendGridAPIClient(api_key=sg_api_key)
        from_email = Email(settings.GMAIL_USER)
        to_email = To(to)
        subject = "Your Sales Insight Report — Rabbitt AI"
        content = Content("text/html", _build_html(summary))
        mail = Mail(from_email, to_email, subject, content)

        # Attach charts if present
        if charts:
            for filename, chart_bytes in charts.items():
                encoded = base64.b64encode(chart_bytes).decode()
                attachment = Attachment()
                attachment.file_content = FileContent(encoded)
                attachment.file_type = FileType("image/png")
                attachment.file_name = FileName(filename)
                attachment.disposition = Disposition("attachment")
                mail.add_attachment(attachment)

        try:
            response = sg.send(mail)
            if response.status_code >= 200 and response.status_code < 300:
                logger.info("SendGrid fallback email dispatched to %s", to)
            else:
                logger.error("SendGrid fallback failed: %s", response.body)
                raise EmailError()
        except Exception as sg_e:
            logger.error("SendGrid fallback exception: %s", sg_e)
            raise EmailError()
