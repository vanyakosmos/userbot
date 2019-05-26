import asyncio
import re
from time import time

from .utils import handle_help, Event


def format_time(sec: float):
    sec = int(sec)
    m = sec // 60
    s = sec % 60
    return f'{m:02d}:{s:02d}'


async def timer(event: Event):
    if await handle_help(event):
        return

    args = event.pattern_match
    t = args.time
    message = args.message

    if not re.match(r'\d+', t):
        return
    sec = int(t)
    if sec > 60 * 60:
        return
    initial = time()
    cur = time()
    text = ''

    while cur - initial < sec:
        cur = time()
        dif = initial + sec - cur
        t = format_time(dif)
        new_text = f'⏱ `{t}`'
        if text != new_text:
            await asyncio.gather(
                event.edit(text=new_text),
                asyncio.sleep(1),
            )
            text = new_text
    if not message:
        message = f"🔥 Time's up! {sec}s"
    await asyncio.gather(
        event.delete(),
        event.respond(message),
    )
