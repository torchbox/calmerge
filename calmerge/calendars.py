import asyncio
from datetime import timedelta

import icalendar
from aiocache import Cache
from aiohttp import ClientSession

from .config import CalendarConfig

fetch_cache = Cache(Cache.MEMORY, ttl=3600)


async def fetch_calendar(session: ClientSession, url: str) -> icalendar.Calendar:
    cache_key = "calendar_" + url
    cached_calendar_data = await fetch_cache.get(cache_key)

    if cached_calendar_data is None:
        response = await session.get(url)
        cached_calendar_data = await response.text()
        await fetch_cache.set(cache_key, cached_calendar_data)

    return icalendar.Calendar.from_ical(cached_calendar_data)


async def fetch_merged_calendar(calendar_config: CalendarConfig) -> icalendar.Calendar:
    merged_calendar = icalendar.Calendar()

    async with ClientSession() as session:
        calendars = [fetch_calendar(session, str(url)) for url in calendar_config.urls]

        for coro in asyncio.as_completed(calendars):
            calendar = await coro
            for component in calendar.walk("VEVENT"):
                merged_calendar.add_component(component)

    return merged_calendar


def offset_calendar(calendar: icalendar.Calendar, offset_days: int) -> None:
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
