from enum import Enum


class WSType(Enum):
    PING = "ping"
    USER_NOTIFICATION = "user_notification"
    MESSAGE_READ = "message_read"
    UNKNOWN = "unknown"