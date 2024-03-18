async def test_health_view(client):
    response = await client.get("/.health/")
    assert response.status == 200
    assert await response.text() == ""
