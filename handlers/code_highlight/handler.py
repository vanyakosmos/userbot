import asyncio
import contextlib
import logging
import urllib.parse
from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter
from pygments.formatters.img import ImageFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from telethon.tl.custom import Message

from handlers.utils import Event, log
from .themes import AppleDark, MonokaiDark

FONTS = ['menlo', 'courier new', None]

logger = logging.getLogger(__name__)


def get_image_formatter(line_numbers: bool, theme: str):
    for font in FONTS:
        try:
            return ImageFormatter(
                image_format="PNG",
                font_size=32,
                font_name=font,
                image_pad=30,
                line_numbers=line_numbers,
                line_number_bg='#22231e',
                line_number_fg='#ddd',
                line_number_bold=False,
                line_number_separator=True,
                line_number_pad=10,
                style=MonokaiDark if theme == 'monokai' else AppleDark,
            )
        except Exception as e:
            logger.exception(e)
    else:
        fonts = ', '.join(FONTS)
        logger.error(f"Unable to find any of listed fonts: {fonts}")
        return


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


def generate_code_image(code: str, lang: Optional[str] = None, line_numbers=True, theme='monokai'):
    formatter = get_image_formatter(line_numbers, theme)
    lexer = get_lexer(code=code, lang=lang)
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


def get_code_image(
    code: str,
    lang: Optional[str] = None,
    line_numbers=True,
    theme='monokai',
) -> Image.Image:
    image = generate_code_image(code, lang, line_numbers, theme)
    image = add_corners(image, 10)
    image = add_shadow(image)
    return image


@contextlib.contextmanager
def load_image(
    code: str,
    lang: Optional[str] = None,
    line_numbers=True,
    add_carbon_link=True,
    theme='monokai',
):
    if not code:
        raise ValueError('Code block is empty.')
    for line in code.split('\n'):
        if len(line) > 150:
            raise ValueError('Line are to long.')
    image = get_code_image(code, lang, line_numbers, theme)
    file = BytesIO()
    image.save(file, 'PNG')
    file.seek(0)
    file.name = 'foo.png'
    link = build_carbon_url(code, lang)
    link = f'[carbon]({link})' if len(link) < 1000 and add_carbon_link else None
    yield file, link
    file.close()
    image.close()


async def send_image(
    event,
    action,
    code: str,
    lang: Optional[str] = None,
    line_numbers=True,
    add_carbon_link=True,
    theme='monokai',
):
    try:
        with load_image(code, lang, line_numbers, add_carbon_link, theme) as (file, link):
            await asyncio.gather(
                action(link, file=file) if link else action(file=file),
                event.delete(),
            )
    except ValueError as e:
        print('error:', e)
        await event.delete()


@log
async def highlight_code(event: Event):
    args = event.pattern_match
    reply_msg = await event.get_reply_message()  # type: Message
    if reply_msg and reply_msg.text:
        await send_image(
            event,
            reply_msg.reply,
            reply_msg.raw_text,
            # treat .text as language hint because we don't need it anyway
            lang=args.lang or args.text,
            line_numbers=args.line_numbers,
            add_carbon_link=args.carbon,
            theme=args.theme,
        )
    elif args.text:
        code = args.text.strip()
        await send_image(
            event,
            event.respond,
            code,
            lang=args.lang,
            line_numbers=args.line_numbers,
            add_carbon_link=args.carbon,
            theme=args.theme,
        )


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
