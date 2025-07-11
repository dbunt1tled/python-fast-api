from pydantic import BaseModel, BeforeValidator
from typing import Annotated
import re

def validate_jwt_format(v: str) -> str:
    jwt_pattern = r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$'

    if not re.match(jwt_pattern, v):
        raise ValueError('Invalid JWT format. Expected format: header.payload.signature')

    parts = v.split('.')
    if len(parts) != 3:
        raise ValueError('JWT must have exactly 3 parts separated by dots')

    for i, part in enumerate(parts):
        if not part:
            raise ValueError(f'JWT part {i+1} is empty')

    return v

JWTToken = Annotated[str, BeforeValidator(validate_jwt_format)]
