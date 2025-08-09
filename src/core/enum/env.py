from enum import Enum


class Env(str, Enum):
    DEVELOP = "dev"
    STAGE = "stage"
    PRODUCTION = "prod"
