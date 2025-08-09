import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import NotFoundException
from src.core.service.email.email import EMessage


class EmailService:
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        app_password: str,
        from_email: str,
    ) -> None:
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.app_password = app_password

    def send_email(self, message: EMessage) -> None:
        msg = MIMEMultipart()
        msg["From"] = self.from_email
        msg["To"] = message.to if isinstance(message.to, str) else ", ".join(message.to)
        msg["Subject"] = message.subject
        if message.cc:
            msg["Cc"] = ", ".join(message.cc)

        if message.bcc:
            msg["Bcc"] = ", ".join(message.bcc)

        msg.attach(MIMEText(message.body, message.body_type))

        if message.attachments:
            for file_path in message.attachments:
                file = Path(file_path)
                if not file.exists():
                    raise NotFoundException(
                        error_no=ErrorNo.EMAIL_ATTACHMENT_NOT_FOUND, message=f"File not found: {file_path}"
                    )
                msg.attach(EmailService._attach_file(file))

        self._send_message(msg, message.to)

    @staticmethod
    def _attach_file(file_path: Path) -> MIMEBase:
        filename = file_path.name
        ext = file_path.suffix.lower()
        if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp"]:
            with open(file_path, "rb") as f:
                attachment = MIMEImage(f.read())
                attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

        elif ext == ".pdf":
            with open(file_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

        elif ext in [".doc", ".docx"]:
            with open(file_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="msword")
                attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

        elif ext in [".xls", ".xlsx"]:
            with open(file_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="vnd.ms-excel")
                attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

        else:
            with open(file_path, "rb") as f:
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header("Content-Disposition", f"attachment; filename= {filename}")

        return attachment

    def _send_message(self, msg: MIMEMultipart, to_email: str | list[str]) -> None:
        recipients = [to_email] if isinstance(to_email, str) else to_email

        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            server.login(self.from_email, self.app_password)
            server.sendmail(self.from_email, recipients, msg.as_string())
