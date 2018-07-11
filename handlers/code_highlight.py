import asyncio
import contextlib
import urllib.parse
from io import BytesIO
from typing import Optional, Union

from PIL import Image, ImageDraw, ImageFilter
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


def generate_code_image(code: str, lang: Optional[str] = None, line_numbers=True):
    lexer = get_lexer(code=code, lang=lang)
    formatter = ImageFormatter(
        image_format="PNG",
        font_size=32,
        image_pad=30,
        line_numbers=line_numbers,
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
    image = Image.open(file).convert('RGBA')
    return image


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im


def add_shadow(im: Image.Image, pad=100):
    # bg
    w, h = im.size
    back = Image.new('RGBA', (w + pad, h + pad), '#fff')
    # shadow
    off = pad // 2
    back.paste((0, 0, 0, 100), (
        off - 10,
        off + 20,
        w + off + 10,
        h + off + 20,
    ))
    for i in range(10):
        back = back.filter(ImageFilter.BLUR)
    # image
    off = pad // 2
    back.paste(im, (off, off), mask=im)
    return back


def get_code_image(code: str, lang: Optional[str] = None, line_numbers=True) -> Image.Image:
    image = generate_code_image(code, lang, line_numbers)
    image = add_corners(image, 10)
    image = add_shadow(image)
    return image


@contextlib.contextmanager
def load_image(code: str, lang: Optional[str] = None, line_numbers=True):
    if not code:
        raise ValueError('Code block is empty.')
    for line in code.split('\n'):
        if len(line) > 150:
            raise ValueError('Line are to long.')
    image = get_code_image(code, lang, line_numbers)
    file = BytesIO()
    image.save(file, 'PNG')
    file.seek(0)
    file.name = 'foo.png'
    link = build_carbon_url(code, lang)
    link = f'[carbon]({link})' if len(link) < 1000 else None
    yield file, link
    file.close()
    image.close()


async def send_image(event, action, code: str,
                     lang: Optional[str] = None,
                     line_numbers=True):
    try:
        with load_image(code, lang, line_numbers) as (file, link):
            await asyncio.gather(
                action(link, file=file),
                event.delete(),
            )
    except ValueError:
        await event.delete()


async def highlight_code(event):
    code = event.pattern_match.group(1)
    code = code.strip()
    await send_image(event, event.respond, code)


async def highlight_reply(event: Union[Message, NewMessage.Event]):
    line_numbers = event.pattern_match.group(1) is not None
    lang = event.pattern_match.group(2)
    reply_msg = await event.get_reply_message()  # type: Message
    if reply_msg:
        code = reply_msg.raw_text
        await send_image(event, reply_msg.reply, code, lang, line_numbers)


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
