import sys
from typing import Any


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    DARK_GRAY = "\033[90m"

    BG_RED = "\033[41m"

    RED_WHITE = "\033[41m\033[37m"
    GREEN_WHITE = "\033[42m\033[37m"
    YELLOW_WHITE = "\033[43m\033[37m"
    BLUE_WHITE = "\033[44m\033[37m"
    MAGENTA_WHITE = "\033[45m\033[37m"
    CYAN_WHITE = "\033[46m\033[37m"
    WHITE_WHITE = "\033[47m\033[37m"

    LEVEL_COLORS = {
        'DEBUG': "🐛 " + GREEN_WHITE + BOLD + " DEBUG " + RESET,
        'INFO': "💡 " + YELLOW_WHITE + BOLD + " INFO " + RESET,
        'WARNING': "⚠️ " + YELLOW_WHITE + BOLD + " WARNING " + RESET,
        'ERROR': "❌ " + RED_WHITE + BOLD + " ERROR " + RESET,
        'CRITICAL': "🚨 " + MAGENTA_WHITE + BOLD + " CRITICAL " + RESET,
    }

    @staticmethod
    def is_supported() -> bool:
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    @staticmethod
    def colorize_value(value: Any) -> str:
        if isinstance(value, str):
            return f'{Colors.BRIGHT_GREEN}"{value}"{Colors.RESET}'
        elif isinstance(value, (int, float)):
            return f"{Colors.BRIGHT_BLUE}{value}{Colors.RESET}"
        elif isinstance(value, bool):
            return f"{Colors.BRIGHT_YELLOW}{value}{Colors.RESET}"
        elif value is None:
            return f"{Colors.DARK_GRAY}null{Colors.RESET}"
        elif isinstance(value, (list, dict)):
            return f"{Colors.BRIGHT_MAGENTA}{str(value)}{Colors.RESET}"
        else:
            return f"{Colors.BRIGHT_MAGENTA}{str(value)}{Colors.RESET}"

