from telethon.events import StopPropagation

from config import USERBOT_NAME
from .utils import Event, log

__all__ = ['handle_help', 'handle_nou', 'handle_hello']


@log
async def handle_hello(event: Event):
    await event.reply(f'hello from {USERBOT_NAME}')


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
