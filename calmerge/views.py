from aiohttp import web


async def healthcheck(request):
    return web.Response(text="")
