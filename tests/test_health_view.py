from aiohttp.test_utils import TestClient


async def test_health_view(client: TestClient) -> None:
    response = await client.get("/.health/")
    assert response.status == 200
    assert await response.text() == ""
