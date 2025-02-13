import asyncio
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

import icalendar
from aiocache import Cache
from aiohttp import ClientSession
from mergecal import merge_calendars

from .config import CalendarConfig

fetch_cache = Cache(Cache.MEMORY, ttl=3600)

PRODID = "-//Torchbox//Calmerge//EN"


async def fetch_calendar(session: ClientSession, url: str) -> icalendar.Calendar:
    cache_key = "calendar_" + url
    cached_calendar_data = await fetch_cache.get(cache_key)

    if cached_calendar_data is None:
        response = await session.get(url)
        cached_calendar_data = await response.text()
        await fetch_cache.set(cache_key, cached_calendar_data)

    return icalendar.Calendar.from_ical(cached_calendar_data)


async def fetch_merged_calendar(calendar_config: CalendarConfig) -> icalendar.Calendar:
    calendars = []

    async with ClientSession() as session:
        for coro in asyncio.as_completed(
            [fetch_calendar(session, str(url)) for url in calendar_config.urls]
        ):
            calendars.append(await coro)

    return merge_calendars(calendars, prodid=PRODID)


def shift_event_by_offset(event: icalendar.cal.Component, offset: timedelta) -> None:
    """
    Mutate a calendar event and shift its dates to a given offset
    """
    if "DTSTART" in event:
        event["DTSTART"].dt += offset
    if "DTEND" in event:
        event["DTEND"].dt += offset


def create_offset_calendar_events(
    calendar: icalendar.Calendar, duplicate_days: list[int]
) -> None:
    """
    Mutate a calendar and add additional events at given offsets
    """
    new_components = []
    for component in calendar.walk("VEVENT"):
        for days in duplicate_days:
            day_component = deepcopy(component)

            # Create a new ID so calendar software shows it as a different event
            day_component["UID"] = str(uuid4())

            shift_event_by_offset(day_component, timedelta(days=days))

            if "SUMMARY" in day_component:
                day_component["SUMMARY"] += (
                    f" ({abs(days)} days {'after' if days > 0 else 'before'})"
                )

            if "DESCRIPTION" in day_component:
                day_component["DESCRIPTION"] += (
                    f"\n\nNote: This event has been offset {days} days."
                )

            new_components.append(day_component)

    for component in new_components:
        calendar.add_component(component)


def set_calendar_metadata(
    calendar: icalendar.Calendar, calendar_config: CalendarConfig
) -> None:
    """
    Mutate a calendar to set metadata based on config
    """

    if calendar_config.name:
        calendar.add("X-WR-CALNAME", calendar_config.name)

    if calendar_config.description:
        calendar.add("X-WR-CALDESC", calendar_config.description)

    calendar.add(
        "X-PUBLISHED-TTL",
        icalendar.vDuration(timedelta(hours=calendar_config.ttl_hours)),
    )
