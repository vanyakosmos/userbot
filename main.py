import logging

from telethon import TelegramClient
from telethon.events import NewMessage

import handlers
from settings import API_HASH, API_ID, NOU_LIST, USER_PASSWORD, USER_PHONE


logging.basicConfig(level=logging.WARNING)
client = TelegramClient('userbot', API_ID, API_HASH)

outgoing_handlers = [
    (handlers.calculator, r'eval (.+)'),
    (handlers.sub, r's/(.*)/(.*)/?'),
    (handlers.boop, r'boopv?'),
    (handlers.timer, r'timer (\d+)'),
    (handlers.highlight_own, r'code([\w\W]+)'),
    (handlers.highlight_reply, r'high(\w+)?'),
]
for callback, pattern in outgoing_handlers:
    client.add_event_handler(callback, NewMessage(outgoing=True, pattern=pattern))

nou_pattern = "|".join(NOU_LIST)
nou_pattern = '(' + nou_pattern + ')'
other_handlers = [
    (handlers.nou, nou_pattern),
]
for callback, pattern in other_handlers:
    client.add_event_handler(callback, NewMessage(pattern=pattern))

if __name__ == '__main__':
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
