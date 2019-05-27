from telethon.events import StopPropagation

from .utils import Event


async def handle_help(event: Event):
    args = event.pattern_match
    if getattr(args, 'help', None) is not None:
        text = args.help.strip()
        text = f"```{text}```"
        await event.reply(text)
        raise StopPropagation()


async def nou(event: Event):
    await event.reply('no u')
