from aiohttp import web

from .calendars import fetch_merged_calendar, offset_calendar


async def healthcheck(request):
    return web.Response(text="")


async def calendar(request):
    config = request.app["config"]

    calendar_config = config.get_calendar_by_name(request.match_info["name"])

    if calendar_config is None:
        return web.HTTPNotFound()

    calendar = await fetch_merged_calendar(calendar_config)

    if offset := calendar_config.offset:
        offset_calendar(calendar, offset)

    return web.Response(body=calendar.to_ical(sorted=True))
