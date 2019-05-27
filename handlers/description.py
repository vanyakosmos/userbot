import asyncio
import logging
import random

from telethon.tl.functions.account import UpdateProfileRequest

from .utils import Event

logger = logging.getLogger(__name__)
STATUS = {
    'desc': False,
}


async def loop_description(event: Event):
    status = not STATUS['desc']
    STATUS['desc'] = status
    status_text = 'start' if status else 'end'
    await event.respond(f"loop desc: {status_text}")
    while STATUS['desc']:
        r = random.randint(0, 666)
        about = f'roll {r}'
        update_req = UpdateProfileRequest(about=about)
        logger.debug(f"new description: {about!r}")
        await event.client(update_req)
        await asyncio.sleep(5)
