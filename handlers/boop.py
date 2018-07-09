import asyncio
import glob
from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message


async def boop(event: Union[Message, NewMessage.Event]):
    await event.delete()
    video = event.raw_text.endswith('v')

    images = glob.glob('data/boop/out*.png')
    images = sorted(images)
    im_len = len(images)

    texts = 'boop **BOOP**'.split()
    texts_len = len(texts)

    if video:
        message = await event.respond(texts[0], file='data/boop/doge.mp4')
    else:
        message = await event.respond(texts[0], file=images[0])
    loops = 3
    for i in range(im_len * loops - 1):
        text = texts[(i + 1) % texts_len]
        image = None if video else images[(i + 1) % im_len]
        await asyncio.gather(
            message.edit(text=text, file=image),
            asyncio.sleep(0.333),
        )
    await message.delete()
