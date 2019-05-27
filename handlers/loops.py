import asyncio
import logging
import random
from datetime import datetime

from telethon.tl.functions.account import UpdateProfileRequest

from config import NAME
from .utils import Event

logger = logging.getLogger(__name__)
STATUS = {
    'description': False,
    'username': False,
}


async def loop_description(event: Event):
    text_type = event.pattern_match.type or 'time'
    sleep = event.pattern_match.sleep
    status = not STATUS['description']
    STATUS['description'] = status
    if status:
        await event.reply(f"will change description every {sleep}s")
    else:
        await event.reply(f"stop")
    while STATUS['description']:
        if text_type == 'time':
            t = datetime.utcnow()
            about = t.strftime('¿ %Y/%m/%d %H:%M UTC ?')
        elif text_type == 'roll':
            r = random.randint(0, 666)
            about = f'roll {r}'
        else:
            await event.reply(f"unknown text type {text_type!r}")
            return
        logger.debug(f"new description: {about!r}")
        await event.client(UpdateProfileRequest(about=about))
        await asyncio.sleep(sleep)


def random_capitalization(text):
    tl = list(text)
    for i in random.sample(range(len(text)), random.randint(0, len(text) - 1)):
        if tl[i].islower():
            tl[i] = tl[i].upper()
        else:
            tl[i] = tl[i].lower()
    text = ''.join(tl)
    return text


async def loop_name(event: Event):
    sleep = event.pattern_match.sleep
    status = not STATUS['username']
    STATUS['username'] = status
    if status:
        await event.reply(f"will change name every {sleep}s")
    else:
        await event.reply(f"stop")
    while STATUS['username']:
        name = random_capitalization(NAME)
        if random.random() > 0.66:
            name = NAME[::-1]
        logger.debug(f"new name: {name!r}")
        await event.client(UpdateProfileRequest(first_name=name))
        await asyncio.sleep(sleep)
