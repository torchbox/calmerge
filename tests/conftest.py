from pathlib import Path

import pytest

from calmerge import get_aiohttp_app
from calmerge.config import Config


@pytest.fixture
def config() -> Config:
    return Config.from_file(Path(__file__).resolve().parent / "calendars.toml")


@pytest.fixture
def client(event_loop, aiohttp_client, config):
    return event_loop.run_until_complete(aiohttp_client(get_aiohttp_app(config)))
