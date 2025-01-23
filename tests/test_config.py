import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError
from tomllib import TOMLDecodeError

from calmerge.config import MAX_OFFSET, AuthConfig, CalendarConfig, Config


def test_non_unique_urls() -> None:
    with pytest.raises(ValidationError) as e:
        CalendarConfig(slug="test", urls=["https://example.com"] * 10)  # type: ignore [list-item]

    assert e.value.errors()[0]["msg"] == "URLs must be unique"


def test_non_unique_offset_days() -> None:
    with pytest.raises(ValidationError) as e:
        CalendarConfig(
            slug="test",
            urls=["https://example.com"],  # type: ignore [list-item]
            offset_days=[1, 2, 3, 2, 1],
        )

    assert e.value.errors()[0]["msg"] == "Offset days must be unique"


def test_invalid_offset_days() -> None:
    with pytest.raises(ValidationError) as e:
        CalendarConfig(
            slug="test",
            urls=["https://example.com"],  # type: ignore [list-item]
            offset_days=[MAX_OFFSET + 1],
        )

    assert (
        e.value.errors()[0]["msg"]
        == f"Offset days must be between -{MAX_OFFSET} and {MAX_OFFSET}"
    )


def test_duplicate_calendar_slug() -> None:
    calendar_config = CalendarConfig(slug="test", urls=["https://example.com"])  # type: ignore [list-item]

    with pytest.raises(ValidationError) as e:
        Config(calendar=[calendar_config] * 5)

    assert e.value.errors()[0]["msg"] == "Calendar slugs must be unique"


def test_urls_expand_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FOO", "BAR")

    calendar_config = CalendarConfig(
        slug="test",
        urls=["https://example.com/$FOO"],  # type: ignore [list-item]
    )

    assert str(calendar_config.urls[0]) == "https://example.com/BAR"


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


def test_validate_config_command(tmp_path: Path, config_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "calmerge", "--config", str(config_path), "validate"],
        stdout=subprocess.PIPE,
    )
    assert result.returncode == 0
    assert result.stdout == b"Config is valid!\n"


def test_validate_config_command_invalid_config() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "calmerge",
            "--config",
            str(Path(__file__).resolve()),
            "validate",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 1


def test_validate_config_command_missing_file(tmp_path: Path) -> None:
    test_config_file = tmp_path / "test.toml"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "calmerge",
            "--config",
            str(test_config_file),
            "validate",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode == 2


def test_default_listing_config() -> None:
    config = Config()
    assert not config.listing.enabled
