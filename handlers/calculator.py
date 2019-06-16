import asyncio
import logging
import re

from .utils import Event, log

__all__ = ['handle_eval']
logger = logging.getLogger(__name__)


@log
async def handle_eval(event: Event):
    expr = event.pattern_match.expression
    logger.debug(f'expr: {expr}')
    expr = re.sub(r'\^', r'**', expr)
    expr = re.sub(r'[^\d+\-*/().,%&|{}\[\]\s]', '', expr)

    if not 0 < len(expr) < 100:
        await event.reply("Bad expression.")
        return
    try:
        answer = eval(expr)
        if answer == set():
            answer = '{}'
        msg = f'```{expr}\n> {answer}```'
    except Exception as e:
        logger.error(f"error in expression: {expr}")
        logger.exception(e)
        msg = f"`{expr}`\nBad expression."
    await asyncio.gather(
        event.delete(),
        event.respond(msg),
    )
