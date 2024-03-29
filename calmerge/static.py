import asyncio
from pathlib import Path

from .calendars import fetch_merged_calendar, offset_calendar
from .config import CalendarConfig


def write_calendar(calendar_config: CalendarConfig, output_file: Path) -> None:
    merged_calendar = asyncio.run(fetch_merged_calendar(calendar_config))

    if offset_days := calendar_config.offset_days:
        offset_calendar(merged_calendar, offset_days)

    output_file.write_bytes(merged_calendar.to_ical())
