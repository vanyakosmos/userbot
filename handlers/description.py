import asyncio
import random

from telethon.tl.functions.account import UpdateProfileRequest

from .utils import Event, handle_help
from settings import STATUS


async def loop_description(event: Event):
    if await handle_help(event):
        return

    status = not STATUS['desc']
    STATUS['desc'] = status
    status_text = 'start' if status else 'end'
    await event.respond(f"loop desc: {status_text}")
    while STATUS['desc']:
        r = random.randint(0, 1000)
        about = f'roll {r}'
        update_req = UpdateProfileRequest(about=about)
        await event.respond(f"about: {about}")
        await event.client(update_req)
        await asyncio.sleep(5)
