from datetime import timedelta

import icalendar
import pytest
from aiohttp import BasicAuth
from aiohttp.test_utils import TestClient

from calmerge.config import MAX_OFFSET


async def test_retrieves_calendars(client: TestClient) -> None:
    response = await client.get("/python.ics")
    assert response.status == 200

    calendar = icalendar.Calendar.from_ical(await response.text())
    assert not calendar.is_broken


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


@pytest.mark.parametrize("offset", [100, -100, MAX_OFFSET, -MAX_OFFSET])
async def test_custom_offset(client: TestClient, offset: int) -> None:
    offset_response = await client.get(
        "/python-custom-offset.ics",
        params={"offset_days": offset},
    )
    offset_calendar = icalendar.Calendar.from_ical(await offset_response.text())

    original_response = await client.get("/python.ics")
    original_calendar = icalendar.Calendar.from_ical(await original_response.text())

    assert not offset_calendar.is_broken
    assert not original_calendar.is_broken

    original_events_by_summary = {
        event["SUMMARY"]: event for event in original_calendar.walk("VEVENT")
    }

    delta = timedelta(days=offset)

    for offset_event in offset_calendar.walk("VEVENT"):
        original_event = original_events_by_summary[offset_event["SUMMARY"]]

        assert offset_event["dtstart"].dt == (original_event["dtstart"].dt + delta)

        assert offset_event["dtend"].dt == (original_event["dtend"].dt + delta)

        assert offset_event["dtstamp"].dt == (original_event["dtstamp"].dt + delta)

        assert offset_event["description"] == original_event["description"]


@pytest.mark.parametrize("offset", [MAX_OFFSET + 1, -MAX_OFFSET - 1])
async def test_out_of_bounds_custom_offset(client: TestClient, offset: int) -> None:
    response = await client.get(
        "/python-custom-offset.ics",
        params={"offset_days": offset},
    )

    assert response.status == 400
    assert (
        await response.text()
        == f"400: offset_days is too large (must be between -{MAX_OFFSET} and {MAX_OFFSET})"
    )


@pytest.mark.parametrize("offset", ["invalid", "", "\0"])
async def test_invalid_offset(client: TestClient, offset: str) -> None:
    response = await client.get(
        "/python-custom-offset.ics",
        params={"offset_days": offset},
    )

    assert response.status == 400
    assert await response.text() == "400: offset_days is invalid"
