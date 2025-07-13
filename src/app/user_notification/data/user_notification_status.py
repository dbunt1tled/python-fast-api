from enum import Enum


class UserNotificationStatus(int, Enum):
    NEW = 1
    READ = 2
    INACTIVE = 3
