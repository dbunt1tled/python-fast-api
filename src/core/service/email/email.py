from dataclasses import dataclass, field
from typing import Any


@dataclass
class EMessage:
    to: str | list[str]
    subject: str
    body: str
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    body_type: str = "html"

    def to_dict(self) -> dict[str, Any]:
        return {
            "to": self.to,
            "subject": self.subject,
            "body": self.body,
            "cc": self.cc,
            "bcc": self.bcc,
            "attachments": self.attachments,
            "body_type": self.body_type,
        }
