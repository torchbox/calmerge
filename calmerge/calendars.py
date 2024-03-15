import asyncio
from datetime import timedelta

import icalendar
from aiohttp import ClientSession

from .config import CalendarConfig


async def fetch_calendar(session: ClientSession, url: str):
    response = await session.get(url)

    return icalendar.Calendar.from_ical(await response.text())


async def fetch_merged_calendar(calendar_config: CalendarConfig):
    merged_calendar = icalendar.Calendar()

    async with ClientSession() as session:
        calendars = [fetch_calendar(session, str(url)) for url in calendar_config.urls]

        for coro in asyncio.as_completed(calendars):
            calendar = await coro
            for component in calendar.walk("VEVENT"):
                merged_calendar.add_component(component)

    return merged_calendar


def offset_calendar(calendar: icalendar.Calendar, offset_days: int):
    """
    Mutate a calendar and move events by a given offset
    """
    offset = timedelta(days=offset_days)

    for component in calendar.walk():
        if "DTSTART" in component:
            component["DTSTART"].dt += offset
        if "DTEND" in component:
            component["DTEND"].dt += offset
        if "DTSTAMP" in component:
            component["DTSTAMP"].dt += offset
