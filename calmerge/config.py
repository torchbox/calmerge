from datetime import timedelta
from pathlib import Path
from secrets import compare_digest

import tempora
import tomllib
from aiohttp import BasicAuth
from pydantic import BaseModel, Field, HttpUrl, field_validator


class AuthConfig(BaseModel):
    username: str
    password: str = ""

    def as_basic_auth(self) -> BasicAuth:
        return BasicAuth(self.username, self.password)

    def validate_header(self, auth_header) -> bool:
        try:
            parsed_auth_header = BasicAuth.decode(auth_header)
        except ValueError:
            return False

        return compare_digest(
            self.as_basic_auth().encode(), parsed_auth_header.encode()
        )


class CalendarConfig(BaseModel):
    name: str
    urls: list[HttpUrl]
    offset: timedelta | None = None
    auth: AuthConfig | None = None

    @field_validator("offset", mode="before")
    @classmethod
    def parse_offset(cls, v: str) -> timedelta:
        if v[0] == "-":
            return -tempora.parse_timedelta(v[1:])
        return tempora.parse_timedelta(v)


class Config(BaseModel):
    calendars: list[CalendarConfig] = Field(alias="calendar")

    @classmethod
    def from_file(cls, path: Path):
        with path.open(mode="rb") as f:
            return Config.model_validate(tomllib.load(f))

    def get_calendar_by_name(self, name: str):
        return next(
            (calendar for calendar in self.calendars if calendar.name == name), None
        )
