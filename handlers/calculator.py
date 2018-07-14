import asyncio
import re
from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message


async def calculator(event: Union[Message, NewMessage.Event]):
    expression = event.pattern_match.group(1)
    expression = re.sub(r'[^\d+\-*/().,%&|{}\[\]\s]', '', expression)

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
