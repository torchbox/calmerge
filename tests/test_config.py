import pytest
from pydantic import ValidationError
from pydantic_core import Url

from calmerge.config import AuthConfig, CalendarConfig


def test_non_unique_urls():
    with pytest.raises(ValidationError) as e:
        CalendarConfig(name="test", urls=["https://example.com"] * 10)

    assert e.value.errors()[0]["msg"] == "URLs must be unique"


def test_urls_expand_env_var(monkeypatch):
    monkeypatch.setenv("FOO", "BAR")

    calendar_config = CalendarConfig(name="test", urls=["https://example.com/$FOO"])

    assert calendar_config.urls[0] == Url("https://example.com/BAR")


def test_auth_expand_env_var(monkeypatch):
    monkeypatch.setenv("FOO", "BAR")

    auth_config = AuthConfig(username="$FOO", password="${FOO}BAR")

    assert auth_config.username == "BAR"
    assert auth_config.password == "BARBAR"


def test_expand_unknown_var():
    auth_config = AuthConfig(username="$FOO", password="${FOO}BAR")

    assert auth_config.username == "$FOO"
    assert auth_config.password == "${FOO}BAR"
