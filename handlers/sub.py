import re
from typing import Union

from telethon.events import NewMessage
from telethon.extensions import markdown
from telethon.tl.custom import Message


async def sub(event: Union[Message, NewMessage.Event]):
    pattern_from = event.pattern_match.group(1)
    pattern_from = rf'\b{pattern_from}\b'
    pattern_to = event.pattern_match.group(2)
    pattern_to = f'**{pattern_to}**'

    reply_msg = await event.get_reply_message()  # type: Message
    if reply_msg is None:
        return
    text = reply_msg.raw_text
    new_text = re.sub(pattern_from, pattern_to, text)
    if new_text:
        await event.edit(new_text, parse_mode=markdown)
