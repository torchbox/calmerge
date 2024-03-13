from pydantic import BaseModel, HttpUrl, Field, field_validator
from datetime import timedelta
import tempora
import tomllib
from pathlib import Path


class Calendar(BaseModel):
    name: str
    urls: list[HttpUrl]
    offset: timedelta

    @field_validator("offset", mode="before")
    @classmethod
    def parse_offset(cls, v: str) -> timedelta:
        return tempora.parse_timedelta(v)


class Config(BaseModel):
    calendars: list[Calendar] = Field(alias="calendar")

    @classmethod
    def from_file(cls, path: Path):
        with path.open(mode="rb") as f:
            return Config.model_validate(tomllib.load(f))
