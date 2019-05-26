from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message

Event = Union[Message, NewMessage.Event]


async def handle_help(event):
    args = event.pattern_match
    if getattr(args, 'help', None) is not None:
        text = args.help.strip()
        text = f"```{text}```"
        await event.reply(text)
        return True
    return False
