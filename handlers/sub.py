import re

from telethon.tl.custom import Message

from .utils import Event, log

__all__ = ['handle_sub']


@log
async def handle_sub(event: Event):
    pattern_from = event.pattern_match.a
    pattern_to = event.pattern_match.b or ''

    if pattern_from is None:
        return

    reply_msg = await event.get_reply_message()  # type: Message
    if reply_msg is None:
        return

    text = reply_msg.text
    new_text = re.sub(pattern_from, pattern_to, text)

    if new_text:
        await event.edit(new_text)
