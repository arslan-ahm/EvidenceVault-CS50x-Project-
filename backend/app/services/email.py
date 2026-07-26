"""SMTP email service for EvidenceVault."""

import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: Optional[str] = None,
) -> bool:
    """Send an email via SMTP. Returns True on success, False on failure."""
    settings = get_settings()

    if not settings.smtp_host:
        # Silently skip if SMTP is not configured
        return False

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.email_from
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(text_body or html_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        if settings.smtp_port == 465:
            # Implicit TLS — the connection is encrypted from the start.
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as server:
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        elif settings.smtp_use_tls:
            # Explicit TLS via STARTTLS — the common case (port 587).
            context = ssl.create_default_context()
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                if settings.smtp_username:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
        return True
    except Exception:
        logger.exception("Failed to send email to %s (subject=%r)", to_email, subject)
        return False


def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send a password reset email with a magic link."""
    settings = get_settings()
    reset_url = f"{settings.frontend_reset_url}?token={reset_token}"

    subject = "EvidenceVault — Password Reset Request"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #2563eb, #4f46e5); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
                <h1 style="color: #fff; margin: 0; font-size: 24px;">🔐 Password Reset</h1>
            </div>
            <div style="background: #fff; padding: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">Hello,</p>
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                    We received a request to reset your EvidenceVault password. 
                    Click the button below to create a new password.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background: linear-gradient(135deg, #2563eb, #4f46e5); color: #fff; padding: 14px 36px; border-radius: 12px; text-decoration: none; font-size: 16px; font-weight: 600; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                    If you did not request this, please ignore this email. 
                    This link expires in 1 hour.
                </p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                <p style="color: #9ca3af; font-size: 12px;">
                    EvidenceVault — Responsible Disclosure Intelligence
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_welcome_email(to_email: str, name: str) -> bool:
    """Send a welcome email after registration."""
    subject = "Welcome to EvidenceVault 🛡️"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #2563eb, #4f46e5); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
                <h1 style="color: #fff; margin: 0; font-size: 24px;">🛡️ Welcome to EvidenceVault</h1>
            </div>
            <div style="background: #fff; padding: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">Hi {name},</p>
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                    Welcome to EvidenceVault! Your account has been successfully created.
                    You can now submit vulnerability reports, track cases, and collaborate with the security community.
                </p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{get_settings().frontend_origin}/explore" 
                       style="background: linear-gradient(135deg, #2563eb, #4f46e5); color: #fff; padding: 14px 36px; border-radius: 12px; text-decoration: none; font-size: 16px; font-weight: 600; display: inline-block;">
                        Explore Reports
                    </a>
                </div>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                <p style="color: #9ca3af; font-size: 12px;">
                    EvidenceVault — Responsible Disclosure Intelligence
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)


def send_change_password_notification(to_email: str) -> bool:
    """Notify the user that their password was changed."""
    subject = "EvidenceVault — Password Changed Successfully"
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f4f6f9; margin: 0; padding: 0;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #10b981, #059669); padding: 30px; border-radius: 16px 16px 0 0; text-align: center;">
                <h1 style="color: #fff; margin: 0; font-size: 24px;">✓ Password Updated</h1>
            </div>
            <div style="background: #fff; padding: 30px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">Hi there,</p>
                <p style="color: #374151; font-size: 16px; line-height: 1.6;">
                    Your EvidenceVault password was successfully changed.
                </p>
                <p style="color: #6b7280; font-size: 14px; line-height: 1.6;">
                    If you did not make this change, please contact our support team immediately.
                </p>
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;">
                <p style="color: #9ca3af; font-size: 12px;">
                    EvidenceVault — Responsible Disclosure Intelligence
                </p>
            </div>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, html_body)
