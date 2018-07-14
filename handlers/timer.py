import asyncio
import re
from time import time


def format_time(sec: float):
    sec = int(sec)
    m = sec // 60
    s = sec % 60
    return f'{m:02d}:{s:02d}'


async def timer(event):
    expr = event.pattern_match.group(1).strip().split(maxsplit=1)

    if len(expr) == 2:
        t = expr[0]
        name = expr[1]
    else:
        t = expr[0]
        name = None

    if not re.match('\d+', t):
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
    if name:
        msg = name
    else:
        msg = f"🔥 Time's up! {sec}s"
    await asyncio.gather(
        event.delete(),
        event.respond(msg),
    )
