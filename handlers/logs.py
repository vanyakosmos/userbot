import glob
import os

from config import LOGS_FILE_PATH
from .utils import Event, log

__all__ = ['handle_logs']


@log
async def handle_logs(event: Event):
    file = max(glob.glob(f"{LOGS_FILE_PATH}*"), key=lambda f: os.stat(f).st_mtime)
    size = event.pattern_match.size
    with open(file, 'r') as f:
        lines = f.readlines()[-size:]
    text = ''.join(lines).strip()
    await event.reply(f'```{text}```')
