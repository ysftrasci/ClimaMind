"""SMTP email delivery (no UI dependencies)."""

import smtplib

from climamind.config.settings import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_SENDER_EMAIL,
    SMTP_SENDER_PASSWORD,
)


class EmailError(Exception):
    """Base class for email failures."""


class EmailNotConfiguredError(EmailError):
    """Raised when SMTP credentials are missing or placeholders."""


class EmailAuthenticationError(EmailError):
    """Raised when SMTP login fails."""


class EmailSendError(EmailError):
    """Raised for other send failures."""


class SmtpEmailSender:
    """Sends plain-text email via SMTP (mirrors maincode.py ``send_email``)."""

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        sender_email: str | None = None,
        sender_password: str | None = None,
    ) -> None:
        self._host = host or SMTP_HOST
        self._port = port if port is not None else SMTP_PORT
        self._sender_email = sender_email or SMTP_SENDER_EMAIL
        self._sender_password = sender_password or SMTP_SENDER_PASSWORD

    def send(self, to_email: str, subject: str, body: str) -> None:
        """Deliver a message to *to_email*."""
        self._ensure_configured()
        message = (
            f"Subject: {subject}\n"
            f"To: {to_email}\n"
            f"From: {self._sender_email}\n\n"
            f"{body}"
        )
        try:
            with smtplib.SMTP(self._host, self._port) as smtp:
                smtp.starttls()
                smtp.login(self._sender_email, self._sender_password)
                smtp.sendmail(
                    self._sender_email,
                    to_email,
                    message.encode("utf-8"),
                )
            print(f"✅ Email sent to {to_email}.")
        except smtplib.SMTPAuthenticationError as exc:
            print(f"❌ Mail authentication error for {self._sender_email}.")
            raise EmailAuthenticationError(
                "Email authentication failed. Check settings."
            ) from exc
        except Exception as exc:
            print(f"❌ Mail error for {to_email}: {exc}")
            raise EmailSendError(f"Could not send email: {exc}") from exc

    def _ensure_configured(self) -> None:
        if (
            not self._sender_email
            or not self._sender_password
            or self._sender_password == "YOUR_APP_PASSWORD"
        ):
            print("❌ Email sending is not configured.")
            raise EmailNotConfiguredError("Email sending is not configured.")
