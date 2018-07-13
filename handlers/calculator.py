import re
from typing import Union

from telethon.events import NewMessage
from telethon.tl.custom import Message


async def calculator(event: Union[Message, NewMessage.Event]):
    expression = event.pattern_match.group(1)
    expression = re.sub(r'[^\d+\-*/().%&|{}\[\]]', '', expression)

    if not 0 < len(expression) < 100:
        await event.reply("Bad expression.")
        return
    try:
        answer = eval(expression)
        await event.edit(f'```{expression}\n> {answer}```')
        # await event.reply(f'`{expression} = {answer}`')
    except Exception as e:
        print(expression, e)
        await event.edit(f"`{expression}`\nBad expression.")
