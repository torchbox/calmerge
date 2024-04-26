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
    slug: str
    name: str | None = None
    description: str | None = None
    urls: list[HttpUrl]
    offset_days: list[int] = Field(default_factory=list)
    auth: AuthConfig | None = None
    ttl_hours: int = Field(default=12, gt=0)

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

    @field_validator("offset_days")
    @classmethod
    def validate_offset_days(cls, offset_days: list[int]) -> list[int]:
        if len(set(offset_days)) != len(offset_days):
            raise PydanticCustomError(
                "unique_offset_days", "Offset days must be unique"
            )

        if any(day == 0 for day in offset_days):
            raise PydanticCustomError(
                "zero_offset_days",
                "Offset days must not be zero",
            )

        if not all(-MAX_OFFSET <= day <= MAX_OFFSET for day in offset_days):
            raise PydanticCustomError(
                "offset_days_range",
                f"Offset days must be between -{MAX_OFFSET} and {MAX_OFFSET}",
            )

        return offset_days


class Config(BaseModel):
    calendars: list[CalendarConfig] = Field(alias="calendar", default_factory=list)

    @field_validator("calendars")
    @classmethod
    def validate_unique_calendar_slugs(
        cls, calendars: list[CalendarConfig]
    ) -> list[CalendarConfig]:
        calendar_slugs = {calendar.slug for calendar in calendars}

        if len(calendar_slugs) != len(calendars):
            raise PydanticCustomError("calendar_slugs", "Calendar slugs must be unique")

        return calendars

    @classmethod
    def from_file(cls, path: Path) -> "Config":
        with path.open(mode="rb") as f:
            return Config.model_validate(tomllib.load(f))

    def get_calendar_by_slug(self, slug: str) -> CalendarConfig | None:
        return next(
            (calendar for calendar in self.calendars if calendar.slug == slug), None
        )
