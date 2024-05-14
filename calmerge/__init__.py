import os
from pathlib import Path

import aiohttp_jinja2
import aiohttp_remotes
from aiohttp import web
from jinja2 import FileSystemLoader

from . import templates, views
from .config import Config

STATIC_DIR = Path(__file__).resolve().parent / "static"


def get_aiohttp_app(config: Config) -> web.Application:
    app = web.Application()

    jinja2_env = aiohttp_jinja2.setup(
        app,
        loader=FileSystemLoader(templates.TEMPLATES_DIR),
        context_processors=[
            aiohttp_jinja2.request_processor,
            templates.config_context_processor,
        ],
    )

    app.middlewares.append(
        aiohttp_remotes.XForwardedRelaxed(
            num=int(os.environ.get("X_FORWARDED_NUM", 1))
        ).middleware
    )

    jinja2_env.filters["calendar_url"] = templates.calendar_url

    app["config"] = config

    app.add_routes(
        [
            web.static("/static", STATIC_DIR),
            web.get("/.health/", views.healthcheck, name="healthcheck"),
            web.get("/{slug}.ics", views.calendar, name="calendar"),
            web.get("/{slug}.html", views.calendar_html, name="calendar-html"),
        ]
    )

    if config.listing.enabled:
        app.add_routes([web.get("/all/", views.calendar_listing, name="listing")])

    return app
