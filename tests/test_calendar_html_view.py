from aiohttp import BasicAuth
from aiohttp.test_utils import TestClient


async def test_retrieves_calendars(client: TestClient) -> None:
    response = await client.get("/python.html")
    assert response.status == 200


async def test_unknown_calendar(client: TestClient) -> None:
    response = await client.get("/unknown.html")
    assert response.status == 404


async def test_404_without_auth(client: TestClient) -> None:
    response = await client.get("/python-authed.html")
    assert response.status == 404


async def test_requires_auth(client: TestClient) -> None:
    response = await client.get(
        "/python-authed.html", auth=BasicAuth("user", "password")
    )
    assert response.status == 200


async def test_webcal_url(client: TestClient) -> None:
    response = await client.get("/python.html")
    assert response.status == 200

    text = await response.text()

    assert f"webcal://127.0.0.1:{client.port}/python.ics" in text
    assert f"http://127.0.0.1:{client.port}/python.ics" in text
