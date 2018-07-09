import asyncio
from time import time


def format_time(sec: float):
    sec = int(sec)
    m = sec // 60
    s = sec % 60
    return f'{m:02d}:{s:02d}'


async def timer(event):
    expr = event.pattern_match.group(1)  # type: str
    sec = int(expr.lstrip('0'))
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
    await event.edit(f"🔥 Time's up! > {sec}s")
