from dataclasses import dataclass, field


@dataclass
class EMessage:
    to: str | list[str]
    subject: str
    body: str
    cc: list[str]  = field(default_factory=list)
    bcc: list[str]  = field(default_factory=list)
    attachments: list[str]  = field(default_factory=list)
    body_type: str = "html"