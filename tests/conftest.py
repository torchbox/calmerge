from asyncio import AbstractEventLoop
from pathlib import Path
from typing import Callable

import pytest
from aiohttp.test_utils import TestClient

from calmerge import get_aiohttp_app
from calmerge.config import Config

TEST_CONFIG_PATH = Path(__file__).resolve().parent / "calendars.toml"


@pytest.fixture
def config() -> Config:
    return Config.from_file(TEST_CONFIG_PATH)


@pytest.fixture
def config_path() -> Path:
    return TEST_CONFIG_PATH


@pytest.fixture
def client(
    event_loop: AbstractEventLoop, aiohttp_client: Callable, config: Config
) -> TestClient:
    return event_loop.run_until_complete(aiohttp_client(get_aiohttp_app(config)))  # type: ignore
