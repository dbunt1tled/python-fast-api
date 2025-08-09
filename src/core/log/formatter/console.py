import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.log.colorize import Colors


class ConsoleFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")

    def format(self, record) -> str:
        timestamp = (
            Colors.GREEN
            + datetime.fromtimestamp(record.created, tz=ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M:%S")
            + "(Kyiv)"
            + Colors.RESET
        )
        colored_level = Colors.LEVEL_COLORS.get(record.levelname, record.levelname)
        parts = [f"{colored_level}", f"{timestamp}", record.getMessage()]
        extra_fields = []
        for key, value in record.extra_data.items():
            colored_value = Colors.colorize_value(value)
            extra_fields.append(f"{key}={colored_value}")

        if extra_fields:
            parts.append(f"({', '.join(extra_fields)})")

        return " ".join(parts)
