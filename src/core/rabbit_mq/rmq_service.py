from src.cmd.worker.email.email_action import EmailAction
from src.core.rabbit_mq.producer import AsyncRabbitMQProducer
from src.core.service.email.email import EMessage


class RMQService:
    def __init__(self, producer: AsyncRabbitMQProducer) -> None:
        self.producer = producer

    async def send_email(self, message: EMessage) -> bool:
        return await self.producer.send_message(
            queue_name="p_email",
            action=EmailAction.send_email.value,
            message=message.to_dict(),
            exchange_name="p_email_exchange",
        )