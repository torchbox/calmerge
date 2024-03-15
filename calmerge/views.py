from aiohttp import web

from .calendars import fetch_merged_calendar, offset_calendar


async def healthcheck(request):
    return web.Response(text="")


async def calendar(request):
    config = request.app["config"]

    calendar_config = config.get_calendar_by_name(request.match_info["name"])

    if calendar_config is None:
        raise web.HTTPNotFound()

    if calendar_config.auth and not calendar_config.auth.validate_header(
        request.headers.get("Authorization", "")
    ):
        raise web.HTTPNotFound()

    calendar = await fetch_merged_calendar(calendar_config)

    if offset_days := calendar_config.offset_days:
        offset_calendar(calendar, offset_days)

    return web.Response(body=calendar.to_ical(sorted=True))
