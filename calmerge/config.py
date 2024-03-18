from os.path import expandvars
from pathlib import Path
from secrets import compare_digest

import tomllib
from aiohttp import BasicAuth
from pydantic import BaseModel, Field, HttpUrl, field_validator
from pydantic_core import PydanticCustomError

MAX_OFFSET = 3650


class AuthConfig(BaseModel):
    username: str
    password: str = ""

    @field_validator("*", mode="before")
    @classmethod
    def expand_vars(cls, v: str) -> str:
        return expandvars(v)

    def as_basic_auth(self) -> BasicAuth:
        return BasicAuth(self.username, self.password)

    def validate_header(self, auth_header: str) -> bool:
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

    @field_validator("urls")
    @classmethod
    def check_urls_unique(cls, urls: list[HttpUrl]) -> list[HttpUrl]:
        if len(set(urls)) != len(urls):
            raise PydanticCustomError("unique_urls", "URLs must be unique")
        return urls

    @field_validator("urls", mode="before")
    @classmethod
    def expand_url_vars(cls, urls: list[str]) -> list[str]:
        return [expandvars(url) for url in urls]


class Config(BaseModel):
    calendars: list[CalendarConfig] = Field(alias="calendar", default_factory=list)

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        with path.open(mode="rb") as f:
            return Config.model_validate(tomllib.load(f))

    def get_calendar_by_name(self, name: str) -> CalendarConfig | None:
        return next(
            (calendar for calendar in self.calendars if calendar.name == name), None
        )
