from abc import ABC, abstractmethod

from src.core.di.container import Container
from src.core.rabbit_mq.data import MessageContext, ProcessingResult


class MessageHandler(ABC):
    def __init__(
            self,
            container: Container,
    ) -> None:
        self.container = container
        self.logger = container.log()

    @abstractmethod
    async def handle(self, context: MessageContext) -> ProcessingResult:
        pass

    @abstractmethod
    def can_handle(self, action: str) -> bool:
        pass
