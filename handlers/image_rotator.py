import asyncio
import io
import os

from PIL import Image
from telethon.tl.custom import Message

from .utils import Event, log

__all__ = ['handle_rotate']


@log
async def handle_rotate(event: Event):
    reply_msg = await event.get_reply_message()  # type: Message
    if not reply_msg or not reply_msg.photo:
        return
    im_path = await reply_msg.download_media()
    angle = event.pattern_match.angle
    im = Image.open(im_path)
    im = im.rotate(angle, expand=True)

    with io.BytesIO() as file:
        im.save(file, "PNG")
        file.seek(0)
        await asyncio.gather(
            reply_msg.reply(file=file),
            event.delete(),
        )
    os.remove(im_path)
