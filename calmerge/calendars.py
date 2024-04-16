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


def shift_event_by_offset(event: icalendar.cal.Component, offset: timedelta) -> None:
    """
    Mutate a calendar event and shift its dates to a given offset
    """
    if "DTSTART" in event:
        event["DTSTART"].dt += offset
    if "DTEND" in event:
        event["DTEND"].dt += offset
    if "DTSTAMP" in event:
        event["DTSTAMP"].dt += offset


def create_offset_calendar_events(
    calendar: icalendar.Calendar, duplicate_days: list[int]
) -> None:
    """
    Mutate a calendar and add additional events at given offsets
    """
    new_components = []

    for component in calendar.walk():
        for days in duplicate_days:
            day_component = component.copy()

            shift_event_by_offset(day_component, timedelta(days=days))

            if "SUMMARY" in day_component:
                day_component["SUMMARY"] += (
                    f" ({days} days {'after' if days > 0 else 'before'})"
                )

            new_components.append(day_component)

    for component in new_components:
        calendar.add_component(component)
