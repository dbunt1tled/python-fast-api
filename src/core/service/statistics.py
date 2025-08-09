import os
import time
from datetime import timedelta

import psutil


def memory_usage() -> int:
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    return memory_info.rss  # type: ignore


def format_memory_size(bytes_count: int) -> str:
    base = 1024
    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    if bytes_count == 0:
        return "0 B"

    for i, unit in enumerate(units):
        if bytes_count < base or i == len(units) - 1:
            if i == 0:
                return f"{bytes_count} {unit}"
            else:
                return f"{bytes_count:.1f} {unit}"
        bytes_count /= base  # type: ignore

    return f"{bytes_count:.1f} {units[-1]}"


def format_time(s: int | float) -> str:
    if s < 1:
        if s > 0.001:
            return f"{s * 1000:.2f} ms"
        else:
            return f"{s * 1000000:.0f} us"

    td = timedelta(seconds=s)

    if td.days > 0:
        if td.days == 1:
            return "1 day"
        return f"{td.days} days"

    hours = td.seconds // 3600
    if hours > 0:
        if hours == 1:
            return "1 hr"
        return f"{hours} hrs"

    minutes = (td.seconds % 3600) // 60
    if minutes > 0:
        if minutes == 1:
            return "1 min"
        return f"{minutes} mins"

    seconds = td.seconds % 60
    if seconds == 1:
        return "1 sec"
    return f"{seconds} sec"


def render_statistics(start_time: int | float) -> str:
    duration = format_time(time.time() - start_time)
    memory = format_memory_size(memory_usage())
    cpu = psutil.cpu_percent(interval=1)
    return f"CPU: {cpu}%, memory: {memory}, duration: {duration})"
