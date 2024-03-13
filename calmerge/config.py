from pydantic import BaseModel, HttpUrl, Field, field_validator
from datetime import timedelta
import tempora
import tomllib
from pathlib import Path


class CalendarConfig(BaseModel):
    name: str
    urls: list[HttpUrl]
    offset: timedelta | None = None

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
