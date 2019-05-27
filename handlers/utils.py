import logging
from functools import wraps
from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message

Event = Union[Message, NewMessage.Event]


def log(f):
    @wraps(f)
    async def dec(event):
        logging.getLogger(f.__module__).debug(f"calling {f.__name__!r}")
        await f(event)

    return dec
