import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.core.log.colorize import Colors


class LokiJSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": Colors.GREEN
            + datetime.fromtimestamp(record.created, tz=ZoneInfo("Europe/Kyiv")).strftime("%Y-%m-%d %H:%M:%S")
            + "(Kyiv)"
            + Colors.RESET,
            "level": Colors.LEVEL_COLORS.get(record.levelname, record.levelname),
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "extra_data") and record.extra_data:
            for key, value in record.extra_data.items():
                if isinstance(value, str) and key not in ["timestamp", "level", "logger", "message"]:
                    log_data[key] = Colors.colorize_value(value)
                else:
                    log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)
