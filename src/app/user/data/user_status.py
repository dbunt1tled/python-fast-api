from enum import Enum


class UserStatus(int, Enum):
    PENDING = 1
    ACTIVE = 2
    INACTIVE = 3