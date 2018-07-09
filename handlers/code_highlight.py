import asyncio
import contextlib
import urllib.parse
from io import BytesIO
from typing import Optional, Union

from PIL.Image import Image, open as open_image
from pygments.formatters.img import ImageFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from telethon.events import NewMessage
from telethon.tl.custom import Message

from misc.base16monokai import MonokaiDark


def build_carbon_url(code: str, lang: Optional[str]):
    qs = {
        'bg': 'rgba(37,37,37,1)',
        't': 'base16-dark',
        'wc': 'false',
        'code': code,
        'l': lang or 'auto',
    }
    qs = urllib.parse.urlencode(qs)
    return 'https://carbon.now.sh/?' + qs


def get_lexer(lang=None, code=None):
    if lang:
        return get_lexer_by_name(lang)
    if code:
        return guess_lexer(code, stripall=True)
    raise ValueError("Can't setup lexer.")


def get_code_image(code: str, lang: Optional[str] = None) -> Image:
    lexer = get_lexer(code=code, lang=lang)
    formatter = ImageFormatter(
        image_format="PNG",
        font_size=32,
        image_pad=100,
        line_numbers=True,
        line_number_bg='#22231e',
        line_number_fg='#ddd',
        line_number_bold=False,
        line_number_separator=True,
        line_number_pad=10,
        style=MonokaiDark,
    )
    tokens = lexer.get_tokens(code)
    file = BytesIO()
    formatter.format(tokens, file)
    file.seek(0)
    image = open_image(file)
    return image


def prettify_image(image: Image):
    return image


@contextlib.contextmanager
def load_image(code: str, lang: Optional[str] = None):
    if not code:
        raise ValueError('Code block is empty.')
    for line in code.split('\n'):
        if len(line) > 150:
            raise ValueError('Line are to long.')
    image = get_code_image(code, lang)
    image = prettify_image(image)
    file = BytesIO()
    image.save(file, 'PNG')
    file.seek(0)
    file.name = 'foo.png'
    link = build_carbon_url(code, lang)
    link = f'[carbon]({link})'
    yield file, link
    file.close()
    image.close()


async def send_image(event, action, code: str, lang: Optional[str] = None):
    try:
        with load_image(code, lang) as (file, link):
            await asyncio.gather(
                action(link, file=file),
                event.delete(),
            )
    except ValueError:
        await event.delete()


async def highlight_own(event):
    code = event.pattern_match.group(1)
    code = code.strip()
    await send_image(event, event.respond, code)


async def highlight_reply(event: Union[Message, NewMessage.Event]):
    lang = event.pattern_match.group(1)
    reply_msg = await event.get_reply_message()  # type: Message
    code = reply_msg.raw_text
    await send_image(event, reply_msg.reply, code, lang)


def main():
    code = """
def foo(bar: str):
    a = 43
    b = lambda x: x + 1
    a = b(a)

class Foo(object):
    def hurma(heh):
        heh += 432
        print(heh)
    """
    image = get_code_image(code, 'python')
    image.show()


if __name__ == '__main__':
    main()
