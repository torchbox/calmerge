from datetime import timedelta

import icalendar
from aiohttp import BasicAuth


async def test_retrieves_calendars(client):
    response = await client.get("/python.ics")
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


async def test_404_without_auth(client):
    response = await client.get("/python-authed.ics")
    assert response.status == 404


async def test_requires_auth(client):
    response = await client.get(
        "/python-authed.ics", auth=BasicAuth("user", "password")
    )
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


async def test_offset(client):
    response = await client.get(
        "/python-offset.ics", auth=BasicAuth("user", "password")
    )
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


async def test_offset_calendar_matches(client):
    offset_response = await client.get(
        "/python-offset.ics", auth=BasicAuth("user", "password")
    )
    offset_calendar = icalendar.Calendar.from_ical(await offset_response.text())

    original_response = await client.get(
        "/python.ics", auth=BasicAuth("user", "password")
    )
    original_calendar = icalendar.Calendar.from_ical(await original_response.text())

    assert not offset_calendar.is_broken
    assert not original_calendar.is_broken

    assert len(offset_calendar.walk("VEVENT")) > 1

    assert len(offset_calendar.walk("VEVENT")) == len(original_calendar.walk("VEVENT"))

    original_events_by_summary = {
        event["SUMMARY"]: event for event in original_calendar.walk("VEVENT")
    }

    for offset_event in offset_calendar.walk("VEVENT"):
        original_event = original_events_by_summary[offset_event["SUMMARY"]]

        assert offset_event["dtstart"].dt == (
            original_event["dtstart"].dt + timedelta(days=365)
        )

        assert offset_event["dtend"].dt == (
            original_event["dtend"].dt + timedelta(days=365)
        )

        assert offset_event["dtstamp"].dt == (
            original_event["dtstamp"].dt + timedelta(days=365)
        )

        assert offset_event["description"] == original_event["description"]
