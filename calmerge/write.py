import asyncio
from pathlib import Path

from .calendars import (
    create_offset_calendar_events,
    fetch_merged_calendar,
    set_calendar_metadata,
)
from .config import CalendarConfig


def write_calendar(calendar_config: CalendarConfig, output_file: Path) -> None:
    merged_calendar = asyncio.run(fetch_merged_calendar(calendar_config))

    if offset_days := calendar_config.offset_days:
        create_offset_calendar_events(merged_calendar, offset_days)

    set_calendar_metadata(merged_calendar, calendar_config)

    output_file.write_bytes(merged_calendar.to_ical())
