from aiohttp import web
from . import views
from .config import Config


def get_aiohttp_app(config: Config):
    app = web.Application()
    app["config"] = config

    app.add_routes([web.get("/.health/", views.healthcheck)])

    return app
