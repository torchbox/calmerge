from pathlib import Path
from secrets import compare_digest

import tomllib
from aiohttp import BasicAuth
from pydantic import BaseModel, Field, HttpUrl

MAX_OFFSET = 3650


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
    offset_days: int = Field(default=0, le=MAX_OFFSET, ge=-MAX_OFFSET)
    allow_custom_offset: bool = False
    auth: AuthConfig | None = None


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
