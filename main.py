import logging

from telethon import TelegramClient, events

import handlers
from settings import API_HASH, API_ID, NOU_LIST, USER_PASSWORD, USER_PHONE


logging.basicConfig(level=logging.WARNING)
client = TelegramClient('userbot', API_ID, API_HASH)

nou_pattern = "|".join(NOU_LIST)
nou_pattern = '(' + nou_pattern + ')'
handlers_to_register = [
    (handlers.calculator, events.NewMessage(outgoing=True, pattern=r'^eval (.+)')),
    (handlers.sub, events.NewMessage(outgoing=True, pattern=r'^s/(.*)/(.*)/?$')),
    (handlers.nou, events.NewMessage(pattern=nou_pattern)),
]

for callback, event in handlers_to_register:
    client.add_event_handler(callback, event)

if __name__ == '__main__':
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
