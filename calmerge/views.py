import aiohttp_jinja2
from aiohttp import hdrs, web

from .calendars import (
    create_offset_calendar_events,
    fetch_merged_calendar,
    set_calendar_metadata,
)


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text="")


async def calendar(request: web.Request) -> web.Response:
    config = request.app["config"]

    calendar_config = config.get_calendar_by_slug(request.match_info["slug"])

    if calendar_config is None:
        raise web.HTTPNotFound()

    if calendar_config.auth and not calendar_config.auth.validate_header(
        request.headers.get("Authorization", "")
    ):
        raise web.HTTPNotFound()

    calendar = await fetch_merged_calendar(calendar_config)

    if offset_days := calendar_config.offset_days:
        create_offset_calendar_events(calendar, offset_days)

    set_calendar_metadata(calendar, calendar_config)

    return web.Response(
        body=calendar.to_ical(),
        headers={
            hdrs.CONTENT_TYPE: "text/calendar",
            hdrs.CACHE_CONTROL: f"max-age={calendar_config.ttl_hours * 60 * 60}",
            hdrs.VARY: "Authorization",
            hdrs.CONTENT_DISPOSITION: f"attachment; filename={calendar_config.slug}.ics",
        },
    )


async def calendar_listing(request: web.Request) -> web.Response:
    config = request.app["config"]

    if config.listing.auth and not config.listing.auth.validate_header(
        request.headers.get("Authorization", "")
    ):
        raise web.HTTPUnauthorized(headers={hdrs.WWW_AUTHENTICATE: "Basic"})

    response = aiohttp_jinja2.render_template("listing.html", request, {})
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'unsafe-inline'"
    )
    return response


async def calendar_html(request: web.Request) -> web.Response:
    config = request.app["config"]

    calendar_config = config.get_calendar_by_slug(request.match_info["slug"])

    if calendar_config is None:
        raise web.HTTPNotFound()

    return aiohttp_jinja2.render_template(
        "calendar.html", request, {"calendar": calendar_config}
    )
