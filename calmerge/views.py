from aiohttp import web

from .calendars import fetch_merged_calendar, offset_calendar
from .config import MAX_OFFSET
from .utils import try_parse_int


async def healthcheck(request: web.Request) -> web.Response:
    return web.Response(text="")


async def calendar(request: web.Request) -> web.Response:
    config = request.app["config"]

    calendar_config = config.get_calendar_by_name(request.match_info["name"])

    if calendar_config is None:
        raise web.HTTPNotFound()

    if calendar_config.auth and not calendar_config.auth.validate_header(
        request.headers.get("Authorization", "")
    ):
        raise web.HTTPNotFound()

    calendar = await fetch_merged_calendar(calendar_config)

    if calendar_config.allow_custom_offset and (
        offset_days := try_parse_int(request.query.get("offset_days", ""))
    ):
        if abs(offset_days) > MAX_OFFSET:
            raise web.HTTPBadRequest(
                reason=f"offset_days is too large (must be between -{MAX_OFFSET} and {MAX_OFFSET})"
            )
        offset_calendar(calendar, offset_days)

    elif offset_days := calendar_config.offset_days:
        offset_calendar(calendar, offset_days)

    return web.Response(body=calendar.to_ical(sorted=True))
