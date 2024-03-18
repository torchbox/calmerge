from pathlib import Path

import pytest
from pydantic import ValidationError
from pydantic_core import Url
from tomllib import TOMLDecodeError

from calmerge.config import AuthConfig, CalendarConfig, Config


def test_non_unique_urls() -> None:
    with pytest.raises(ValidationError) as e:
        CalendarConfig(name="test", urls=["https://example.com"] * 10)  # type: ignore [list-item]

    assert e.value.errors()[0]["msg"] == "URLs must be unique"


def test_urls_expand_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOO", "BAR")

    calendar_config = CalendarConfig(
        name="test",
        urls=["https://example.com/$FOO"],  # type: ignore [list-item]
    )

    assert calendar_config.urls[0] == Url("https://example.com/BAR")


def test_auth_expand_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOO", "BAR")

    auth_config = AuthConfig(username="$FOO", password="${FOO}BAR")

    assert auth_config.username == "BAR"
    assert auth_config.password == "BARBAR"


def test_expand_unknown_var() -> None:
    auth_config = AuthConfig(username="$FOO", password="${FOO}BAR")

    assert auth_config.username == "$FOO"
    assert auth_config.password == "${FOO}BAR"


def test_empty_config(tmp_path: Path) -> None:
    test_config_file = tmp_path / "test.toml"
    test_config_file.touch()

    Config.from_file(test_config_file)


def test_invalid_file() -> None:
    with pytest.raises(TOMLDecodeError):
        Config.from_file(Path(__file__).resolve())
