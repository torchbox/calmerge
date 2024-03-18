from asyncio import AbstractEventLoop
from pathlib import Path
from typing import Callable

import pytest
from aiohttp.test_utils import TestClient

from calmerge import get_aiohttp_app
from calmerge.config import Config


@pytest.fixture
def config() -> Config:
    return Config.from_file(Path(__file__).resolve().parent / "calendars.toml")


@pytest.fixture
def client(
    event_loop: AbstractEventLoop, aiohttp_client: Callable, config: Config
) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(get_aiohttp_app(config)))  # type: ignore
