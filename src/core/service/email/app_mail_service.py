

from src.app.user.model.user import User
from src.core.service.dto.token import Token
from src.core.service.email.email import EMessage
from src.core.service.email.email_service import EmailService
from src.core.service.email.view_service import ViewService


class AppMailService:
    def __init__(
            self,
            email_service: EmailService,
            view_service: ViewService,
    ) -> None:
        self.email_service = email_service
        self.view_service = view_service

    async def send_confirm_email(self, user: User, token: Token) -> None:
        body = await self.view_service.render_template("email/confirm_email.html", {"user": user, "token": token.token})
        self.email_service.send_email(message=EMessage(
            to=user.email,
            subject="Welcome to the platform",
            body=body,
        ))


