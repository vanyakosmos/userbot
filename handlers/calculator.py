import asyncio
import re

from .utils import handle_help, Event


async def calculator(event: Event):
    if await handle_help(event):
        return

    expression = re.sub(r'[^\d+\-*/().,%&|{}\[\]\s]', '', event.pattern_match.expression)

    if not 0 < len(expression) < 100:
        await event.reply("Bad expression.")
        return
    try:
        answer = eval(expression)
        if answer == set():
            answer = '{}'
        msg = f'```{expression}\n> {answer}```'
    except Exception as e:
        print(expression, e)
        msg = f"`{expression}`\nBad expression."
    await asyncio.gather(
        event.delete(),
        event.respond(msg),
    )
