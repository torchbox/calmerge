from datetime import timedelta

import icalendar
from aiohttp import BasicAuth
from aiohttp.test_utils import TestClient


async def test_retrieves_calendars(client: TestClient) -> None:
    response = await client.get("/python.ics")
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken

    assert calendar["X-WR-CALNAME"] == "Python"
    assert calendar["X-WR-CALDESC"] == "Python EOL"
    assert calendar["X-PUBLISHED-TTL"] == "PT12H"  # 12 hours

    assert response.headers["Cache-Control"] == "max-age=43200"
    assert response.headers["Content-Disposition"] == "attachment; filename=python.ics"


async def test_unknown_calendar(client: TestClient) -> None:
    response = await client.get("/unknown.ics")
    assert response.status == 404


async def test_404_without_auth(client: TestClient) -> None:
    response = await client.get("/python-authed.ics")
    assert response.status == 404


async def test_requires_auth(client: TestClient) -> None:
    response = await client.get(
        "/python-authed.ics", auth=BasicAuth("user", "password")
    )
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


async def test_offset(client: TestClient) -> None:
    response = await client.get("/python-offset.ics")
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


async def test_offset_calendar_matches(client: TestClient) -> None:
    offset_response = await client.get("/python-offset.ics")
    offset_calendar = icalendar.Calendar.from_ical(await offset_response.text())

    original_response = await client.get("/python.ics")
    original_calendar = icalendar.Calendar.from_ical(await original_response.text())

    assert not offset_calendar.is_broken
    assert not original_calendar.is_broken

    assert (
        len(offset_calendar.walk("VEVENT")) == len(original_calendar.walk("VEVENT")) * 2
    )

    offset_events = [
        event
        for event in offset_calendar.walk("VEVENT")
        if event["SUMMARY"].endswith("(365 days after)")
    ]

    assert len(offset_events) == len(original_calendar.walk("VEVENT"))

    original_events_by_summary = {
        event["SUMMARY"]: event for event in original_calendar.walk("VEVENT")
    }

    for offset_event in offset_events:
        assert offset_event["SUMMARY"].endswith(" (365 days after)")

        original_event = original_events_by_summary[
            offset_event["SUMMARY"].removesuffix(" (365 days after)")
        ]

        assert offset_event["dtstart"].dt == (
            original_event["dtstart"].dt + timedelta(days=365)
        )

        assert offset_event["dtend"].dt == (
            original_event["dtend"].dt + timedelta(days=365)
        )

        assert offset_event["description"].startswith(original_event["description"])
        assert offset_event["description"].endswith(
            "Note: This event has been offset 365 days."
        )
