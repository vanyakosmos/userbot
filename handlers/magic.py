import asyncio
import re

import numpy as np
from numpy.random import choice


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


async def rolled_text(event, text: str, count=3):
    moons = '🌕🌖🌗🌘🌑🌒🌓🌔'
    moons = moons[::-1]
    rounds = len(text) * count
    text_size = len(text)
    text = ''.join(map(widemap.get, text))
    for i in range(rounds):
        msg = ''
        for j in range(text_size):
            msg += moons[(i - j) % len(moons)]
        if i + text_size + 1 >= rounds:
            d = i + text_size - rounds + 1
            msg = text[:d] + msg[d:]
        await asyncio.gather(
            event.edit(msg),
            asyncio.sleep(0.2),
        )


async def magic(event):
    count = int(event.pattern_match.group(1) or '3')
    text = event.pattern_match.group(2)
    await rolled_text(event, text, count)


async def marquee_runner(event, phrase: str, count: int):
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


async def marquee(event):
    count = int(event.pattern_match.group(1) or '3')
    text = event.pattern_match.group(2)
    await marquee_runner(event, text, count)
    await event.edit(text)


async def widener(event):
    text = event.raw_text
    text = ''.join(map(widemap.get, text))
    await event.edit(text)


def main():
    text = magic_matrix('foo')
    print(text)


if __name__ == '__main__':
    main()
