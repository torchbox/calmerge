from aiohttp import BasicAuth
from aiohttp.test_utils import TestClient

from calmerge.config import Config


async def test_listing_view(client: TestClient, config: Config) -> None:
    response = await client.get("/all/", auth=BasicAuth("user", "password"))
    assert response.status == 200


async def test_requires_auth(client: TestClient, config: Config) -> None:
    response = await client.get("/all/")
    assert response.status == 401


async def test_webcal_url(client: TestClient) -> None:
    response = await client.get("/all/", auth=BasicAuth("user", "password"))
    assert response.status == 200

    text = await response.text()

    assert f"webcal://127.0.0.1:{client.port}/python.ics" in text
    assert f"webcal://user:password@127.0.0.1:{client.port}/python-authed.ics" in text
