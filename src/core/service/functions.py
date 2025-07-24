import re
from collections.abc import Generator
from typing import TypeVar

T = TypeVar('T')

invert_case_regex = re.compile(r"(?<!^)(?=[A-Z])")
def chunked(iterable: list[T], size: int) -> Generator[list[T]]:
    for i in range(0, len(iterable), size):
        yield iterable[i:i + size]

def to_invert_case(s: str) -> str:
    s = re.sub(invert_case_regex, '_', s).lower()
    return ' '.join(word.capitalize() for word in s.split('_'))
