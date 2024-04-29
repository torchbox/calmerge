import aiohttp_jinja2
from aiohttp import web
from jinja2 import FileSystemLoader

from . import templates, views
from .config import Config


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

    jinja2_env.filters["webcal_url"] = templates.webcal_url

    app["config"] = config

    app.add_routes(
        [
            web.get("/.health/", views.healthcheck, name="healthcheck"),
            web.get("/{slug}.ics", views.calendar, name="calendar"),
        ]
    )

    if config.listing.enabled:
        app.add_routes([web.get("/all/", views.calendar_listing, name="listing")])

    return app
