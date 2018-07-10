import logging

from telethon import TelegramClient

import handlers
from manager import Manager
from settings import API_HASH, API_ID, NOU_LIST, USERBOT_NAME, USER_PASSWORD, USER_PHONE


STATUS = {
    'up': True,
}

logging.basicConfig(level=logging.WARNING)
client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)

outgoing_handlers = [
    (handlers.calculator, r'^eval (.+)'),
    (handlers.sub, r's/(.*)/(.*)/?'),
    (handlers.boop, r'^boopv?(\d)?$'),
    (handlers.timer, r'^timer (\d+)$'),
    (handlers.highlight_own, r'code([\w\W]+)'),
    (handlers.highlight_reply, r'^high(\w+)?$'),
]

nou_pattern = "|".join(NOU_LIST)
nou_pattern = '(' + nou_pattern + ')'
incoming_handlers = [
    (handlers.nou, nou_pattern),
]

manager = Manager(client)
manager.register_outgoing(*outgoing_handlers)
manager.register_incoming(*incoming_handlers)

if __name__ == '__main__':
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
