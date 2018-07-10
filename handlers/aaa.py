import asyncio
import random
import re


async def raising(event, size=20):
    for i in range(size):
        a = '**A**' + 'a' * i
        a += '\n^\n^'
        await asyncio.gather(
            event.edit(a),
            asyncio.sleep(0.1),
        )


async def random_spikes(event, size=20, times=10):
    for i in range(times):
        chosen = random.sample(range(size), size // 2)
        a = ''
        for j in range(size):
            a += 'a' if j in chosen else 'A'
        a += '\n^\n^'
        await asyncio.gather(
            event.edit(a),
            asyncio.sleep(0.2),
        )


async def running_line(event, phrase: str, count: int):
    pad = '.'
    phrase = phrase.upper()
    phrase = re.sub('\s', pad, phrase)

    size = max(len(phrase) * 2, 10)
    line = phrase + pad * (size - len(phrase))

    for i in range(size * count):
        j = i % size
        text = line[-j:] + line[:-j]
        text = f'`{text}`'
        await asyncio.gather(
            event.edit(text),
            asyncio.sleep(0.5),
        )


async def aaa(event):
    count = int(event.pattern_match.group(1) or '3')
    text = event.pattern_match.group(2)
    await running_line(event, text, count)
    await event.edit(text)
