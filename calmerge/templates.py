from pathlib import Path

import jinja2
from aiohttp import web
from yarl import URL

from .config import CalendarConfig

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


async def config_context_processor(request: web.Request) -> dict:
    return {"config": request.app["config"]}


@jinja2.pass_context
def webcal_url(context: dict, calendar_config: CalendarConfig) -> URL:
    request: web.Request = context["request"]
    config = context["config"]
    calendar_url = context["url"](context, "calendar", slug=calendar_config.slug)

    url = request.url.with_scheme("webcal").with_path(calendar_url.path)

    if config.listing.include_credentials and calendar_config.auth is not None:
        url = url.with_user(calendar_config.auth.username).with_password(
            calendar_config.auth.password
        )

    return url
