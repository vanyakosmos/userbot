import logging
import re
from functools import reduce

from telethon.tl.custom import Message

from .utils import Event, log

__all__ = ['handle_sub']
logger = logging.getLogger(__name__)
FLAGS = {'A', 'I', 'L', 'M', 'S', 'X'}


def parse_sed(value: str):
    sed_parts = value.split('/')
    if len(sed_parts) == 1:
        pattern_from = sed_parts[0]
        pattern_to = ''
        flags = 0
    elif len(sed_parts) == 2:
        pattern_from = sed_parts[0]
        pattern_to = sed_parts[1]
        flags = 0
    else:
        pattern_from, pattern_to, flags, *_ = sed_parts
        flags = flags.upper()
        flags = filter(lambda f: f in FLAGS, flags)
        flags = map(lambda f: getattr(re, f), flags)
        if flags:
            flags = reduce(lambda a, e: a | e, flags)
        else:
            flags = 0
    return pattern_from, pattern_to, flags


@log
async def handle_sub(event: Event):
    args = event.pattern_match
    pattern_from, pattern_to, flags = parse_sed(args.text)
    logger.debug(f"from: {pattern_from}, to: {pattern_to}, flag: {flags}")

    if args.highlight:
        pattern_to = f"**{pattern_to}**"

    reply_msg = await event.get_reply_message()  # type: Message
    if reply_msg is None:
        return

    new_text = re.sub(pattern_from, pattern_to, reply_msg.text, flags=flags)

    if new_text:
        await event.edit(new_text)
