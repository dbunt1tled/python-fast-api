import traceback

from src.cmd.worker.email.email_action import EmailAction
from src.core.rabbit_mq.data import MessageContext, ProcessingResult
from src.core.rabbit_mq.message_handler import MessageHandler
from src.core.service.email.email import EMessage


class SendEmailHandler(MessageHandler):
    def can_handle(self, action: str) -> bool:
        return action in [EmailAction.send_email.value]

    async def handle(self, context: MessageContext) -> ProcessingResult:
        try:
            to = context.payload.get("to")
            subject = context.payload.get("subject")
            body = context.payload.get("body")
            cc = context.payload.get("cc")
            bcc = context.payload.get("bcc")
            body_type = context.payload.get("body_type")
            attachments = context.payload.get("attachments")
            if to is None or subject is None or body is None:
                raise ValueError("🛑 Missing required fields in message")
            self.container.email_service().send_email(
                message=EMessage(
                    to=[str(email) for email in to] if isinstance(to, list) else str(to),
                    cc=[str(email) for email in cc] if isinstance(cc, list) else ([str(cc)] if cc else []),
                    bcc=[str(email) for email in bcc] if isinstance(bcc, list) else ([str(bcc)] if bcc else []),
                    subject=str(subject),
                    body=str(body),
                    body_type=body_type or "html",
                    attachments=[str(attachment) for attachment in attachments]
                    if isinstance(attachments, list)
                    else ([str(attachments)] if attachments else []),
                )
            )
            return ProcessingResult.SUCCESS
        except Exception as e:
            self.logger.error(f"🛑 Failed to send email: {e}", error=traceback.extract_tb(e.__traceback__)[-1])
            return ProcessingResult.REJECT
