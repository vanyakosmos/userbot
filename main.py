import logging

from telethon import TelegramClient

import handlers
from manager import Manager
from persistence import load_session_file, save_before_term
from settings import API_HASH, API_ID, NOU_LIST, USERBOT_NAME, USER_PASSWORD, USER_PHONE


logging.basicConfig(level=logging.WARNING)
save_before_term()
load_session_file()
client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)

outgoing_handlers = [
    (handlers.calculator, r'-e (.+)'),
    (handlers.sub, r'-s/(.*)/(.*)/?'),
    (handlers.boop, r'-boopv?(\d)?'),
    (handlers.timer, r'-t (\d+)'),
    (handlers.highlight_code, r'-c(l)?(c)? ([\w\W]+)'),
    (handlers.highlight_reply, r'-h(l)?(c)?\s?(\w+)?'),
    (handlers.marquee, f'-a(\d+)? (.+)'),
    (handlers.magic, f'-m(\d+)? (.+)'),
]

nou_pattern = "|".join(NOU_LIST)
nou_pattern = '(' + nou_pattern + ')'
incoming_handlers = [
    (handlers.nou, nou_pattern),
]

trashy_handlers = [
    (handlers.widener, f'[^-][0-9a-zA-Z\s_\-\'@^&*%$#.,/+()\[\]"]+'),
]

manager = Manager(client)
manager.register_outgoing(*outgoing_handlers)
manager.register_incoming(*incoming_handlers)
manager.register_trashy(*trashy_handlers)
print('start')

if __name__ == '__main__':
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
