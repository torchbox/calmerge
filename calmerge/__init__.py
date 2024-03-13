from aiohttp import web
from . import views


def get_aiohttp_app():
    app = web.Application()

    app.add_routes([web.get("/.health/", views.healthcheck)])

    return app
