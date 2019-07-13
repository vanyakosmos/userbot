from telethon.events import StopPropagation
from telethon.sessions import SQLiteSession

from config import USERBOT_NAME
from .utils import Event, log

__all__ = ['handle_help', 'handle_nou', 'handle_hello', 'handle_noop']


@log
async def handle_hello(event: Event):
    s = event.client.session
    if isinstance(s, SQLiteSession):
        s = s.filename
    await event.reply(f'{USERBOT_NAME}, session: {s!r}')


@log
async def handle_help(event: Event):
    args = event.pattern_match
    if getattr(args, 'help', None) is not None:
        text = args.help.strip()
        text = f"```{text}```"
        await event.reply(text)
        raise StopPropagation()


@log
async def handle_nou(event: Event):
    await event.reply('no u')


@log
async def handle_noop(_: Event):
    pass
