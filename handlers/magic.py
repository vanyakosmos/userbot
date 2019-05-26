import asyncio
import re
from urllib.parse import quote

import numpy as np
from numpy.random import choice

from handlers.utils import Event

widemap = dict((chr(i), chr(i + 0xFF00 - 0x20)) for i in range(0x21, 0x7F))
widemap[chr(0x20)] = chr(0x3000)  # IDEOGRAPHIC SPACE


def add_border(matrix, border: str):
    x = len(matrix[0])
    matrix = [[border] * x] + matrix + [[border] * x]
    for i, line in enumerate(matrix):
        matrix[i] = [border] + line + [border]
    return matrix


def format(matrix):
    text = '\n'.join(map(''.join, matrix))
    return f'```{text}```'


def add_text(matrix, text: str):
    y = len(matrix)
    x = len(matrix[0])
    l = len(text)
    line = matrix[y // 2]
    start = x // 2 - l // 2
    end = start + l
    line[start:end] = list(map(lambda e: f'{e} ', text))
    return matrix


def magic_matrix(text: str):
    matrix = []
    w = max(int(len(text) * 1.5), 10)
    h = 5
    for y in range(h):
        line = []
        for x in range(w):
            # star = random.choice(a)
            ws = np.array([10, 1], dtype=float)
            ws /= np.sum(ws)
            star = choice(list('🌚🌝'), p=ws)
            line.append(star)
        matrix.append(line)
    # matrix = add_border(matrix, '🌈')
    matrix = add_text(matrix, text)
    text = format(matrix)
    return text


async def sky(event, text: str):
    for i in range(10):
        msg = magic_matrix(text)
        await asyncio.gather(
            event.edit(msg),
            asyncio.sleep(1),
        )


async def rolled_text(event, text: str, count=3, wide=False):
    if not text:
        text = ' ' * 5
    moons = '🌕🌖🌗🌘🌑🌒🌓🌔'
    moons = moons[::-1]
    rounds = len(text) * count
    text_size = len(text)
    if wide:
        text = ''.join(map(widemap.get, text))
    for i in range(rounds):
        msg = ''
        for j in range(text_size):
            msg += moons[(i - j) % len(moons)]
        if i + text_size + 1 >= rounds:
            d = i + text_size - rounds + 1
            msg = text[:d] + msg[d:]
        msg = msg.strip()
        if msg:
            await asyncio.gather(
                event.edit(msg),
                asyncio.sleep(0.2),
            )
        else:
            await event.delete()


async def magic(event: Event):
    args = event.pattern_match
    await rolled_text(event, args.text, args.count, args.wide)


async def marquee_runner(event, phrase: str, count: int):
    pad = '.'
    phrase = re.sub(r'\s', pad, phrase)

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


async def marquee(event: Event):
    args = event.pattern_match
    await marquee_runner(event, args.text, args.count)
    await event.edit(args.text)


async def widener(event):
    text = event.raw_text
    text = ''.join(map(lambda x: widemap.get(x, x), text))
    await event.edit(text)


async def google(event: Event):
    args = event.pattern_match
    if args.let_me:
        base_url = f'http://lmgtfy.com/?q='
    elif args.image:
        base_url = 'https://google.com/search?tbm=isch&q='
    else:
        base_url = 'https://google.com/search?q='

    base_url += quote(args.query)
    msg = f'[{args.query}]({base_url})'
    await event.edit(msg, link_preview=False)


def main():
    text = magic_matrix('foo')
    print(text)


if __name__ == '__main__':
    main()
