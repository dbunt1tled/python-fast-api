from src.app.user.model.user import User
from src.core.rabbit_mq.rmq_service import RMQService
from src.core.service.dto.token import Token
from src.core.service.email.email import EMessage
from src.core.service.email.email_service import EmailService
from src.core.service.email.view_service import ViewService


class AppMailService:
    def __init__(
        self,
        rmq_service: RMQService,
        view_service: ViewService,
    ) -> None:
        self.rmq_service = rmq_service
        self.view_service = view_service

    async def send_confirm_email(self, user: User, token: Token) -> None:
        body = await self.view_service.render_template("email/confirm_email.html", {"user": user, "token": token.token})
        await self.rmq_service.send_email(
            message=EMessage(
                to=user.email,
                subject="Welcome to the platform",
                body=body,
            )
        )
