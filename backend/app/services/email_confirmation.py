import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException, status
from supabase import Client

from app.core.config import get_settings

TOKEN_TTL_HOURS = 24


def create_confirmation(supabase: Client, user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_TTL_HOURS)

    supabase.table("email_confirmations").insert(
        {
            "user_id": user_id,
            "token": token,
            "expires_at": expires_at.isoformat(),
            "confirmed_at": None,
        }
    ).execute()

    return token


def send_confirmation_email(to_email: str, name: str, token: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_email or not settings.app_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SMTP is not configured -- set SMTP_EMAIL/APP_PASSWORD in .env",
        )

    confirm_url = f"{settings.frontend_url}/confirm-email?token={token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Confirm your email for JeevSetu"
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_email}>"
    message["To"] = to_email

    message.attach(MIMEText(_plain_text(name, confirm_url), "plain"))
    message.attach(MIMEText(_html(name, confirm_url), "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        # Gmail app passwords are shown with spaces for readability; strip
        # them since some SMTP AUTH implementations require the raw form.
        server.login(settings.smtp_email, settings.app_password.replace(" ", ""))
        server.send_message(message)


def confirm_token(supabase: Client, token: str) -> dict:
    result = (
        supabase.table("email_confirmations").select("*").eq("token", token).limit(1).execute()
    )
    if not result.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid confirmation link")

    confirmation = result.data[0]

    if confirmation["confirmed_at"] is not None:
        return {"already_confirmed": True}

    expires_at = datetime.fromisoformat(confirmation["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This confirmation link has expired -- sign up again to get a new one",
        )

    supabase.auth.admin.update_user_by_id(confirmation["user_id"], {"email_confirm": True})

    supabase.table("email_confirmations").update(
        {"confirmed_at": datetime.now(timezone.utc).isoformat()}
    ).eq("token", token).execute()

    return {"already_confirmed": False}


def _plain_text(name: str, confirm_url: str) -> str:
    return (
        f"Hi {name},\n\n"
        "Welcome to JeevSetu -- thank you for joining our wildlife conservation community.\n\n"
        f"Confirm your email to finish signing up:\n{confirm_url}\n\n"
        f"This link expires in {TOKEN_TTL_HOURS} hours.\n\n"
        "In partnership with the Bombay Natural History Society (BNHS)."
    )


def _html(name: str, confirm_url: str) -> str:
    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0; padding:0; background-color:#F8F6E9; font-family:Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color:#F8F6E9; padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:480px; background-color:#ffffff; border-radius:16px; overflow:hidden; border:1px solid rgba(11,61,46,0.1);">

            <tr>
              <td style="background-color:#0B3D2E; padding:32px 32px 28px 32px; text-align:center;">
                <div style="font-size:24px; font-weight:bold; color:#F8F6E9; letter-spacing:0.5px;">JeevSetu</div>
                <div style="font-size:13px; color:rgba(248,246,233,0.7); margin-top:6px;">Protect Wildlife. Empower Communities.</div>
              </td>
            </tr>

            <tr>
              <td style="padding:36px 32px 8px 32px;">
                <p style="margin:0 0 16px 0; font-size:16px; color:#0B3D2E;">Hi {name},</p>
                <p style="margin:0 0 24px 0; font-size:15px; line-height:1.6; color:#0B3D2E;">
                  Welcome to <strong>JeevSetu</strong> -- thank you for joining our community dedicated to
                  wildlife conservation and citizen science. Confirm your email address to finish setting
                  up your account.
                </p>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 32px 32px; text-align:center;">
                <a href="{confirm_url}"
                   style="display:inline-block; background-color:#F4C430; color:#0B3D2E; font-weight:bold;
                          font-size:15px; text-decoration:none; padding:14px 36px; border-radius:12px;">
                  Confirm my email
                </a>
              </td>
            </tr>

            <tr>
              <td style="padding:0 32px 32px 32px;">
                <p style="margin:0; font-size:12px; line-height:1.6; color:rgba(11,61,46,0.5);">
                  This link expires in {TOKEN_TTL_HOURS} hours. If the button doesn't work, copy and paste
                  this URL into your browser:<br>
                  <a href="{confirm_url}" style="color:#2E7D32; word-break:break-all;">{confirm_url}</a>
                </p>
              </td>
            </tr>

            <tr>
              <td style="background-color:#F8F6E9; padding:20px 32px; text-align:center; border-top:1px solid rgba(11,61,46,0.08);">
                <p style="margin:0; font-size:12px; color:rgba(11,61,46,0.5);">
                  In partnership with the Bombay Natural History Society (BNHS)
                </p>
              </td>
            </tr>

          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
