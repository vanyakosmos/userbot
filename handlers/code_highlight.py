import asyncio
import contextlib
import urllib.parse
from io import BytesIO
from typing import Optional, Union

from PIL import Image
from picode import picode
from telethon.events import NewMessage
from telethon.tl.custom import Message


BASE_URL = 'https://carbon.now.sh'


def build_url(code: str, lang):
    qs = {
        'bg': 'rgba(37,37,37,1)',
        't': 'base16-dark',
        'wc': 'false',
        'code': code,
        'l': lang or 'auto',
    }
    qs = urllib.parse.urlencode(qs)
    return BASE_URL + '/?' + qs


def build_image(code: str, lang: Optional[str]) -> Image:
    image = picode.to_pic(
        code=code,
        language=lang,
        font_name=picode.DEFAULT_FONT_NAME_WIN,
    )
    return image


@contextlib.contextmanager
def load_image(code: str, lang: Optional[str] = None):
    image = build_image(code, lang)
    file = BytesIO()
    image.save(file, 'PNG')
    file.seek(0)
    file.name = 'foo.png'
    link = build_url(code, lang)
    link = f'[carbon]({link})'
    yield file, link
    file.close()
    image.close()


async def highlight_own(event):
    code = event.pattern_match.group(1)
    code = code.strip()
    with load_image(code) as (file, link):
        await asyncio.gather(
            event.respond(link, file=file),
            event.delete(),
        )


async def highlight_reply(event: Union[Message, NewMessage.Event]):
    lang = event.pattern_match.group(1)
    reply_msg = await event.get_reply_message()  # type: Message
    code = reply_msg.raw_text
    with load_image(code, lang) as (file, link):
        await asyncio.gather(
            reply_msg.reply(link, file=file),
            event.delete(),
        )
