import logging

from telethon import TelegramClient
from telethon.events import NewMessage

import handlers
from settings import API_HASH, API_ID, NOU_LIST, USERBOT_NAME, USER_PASSWORD, USER_PHONE


STATUS = {
    'up': True,
}

logging.basicConfig(level=logging.WARNING)
client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)

outgoing_handlers = [
    (handlers.calculator, r'eval (.+)'),
    (handlers.sub, r's/(.*)/(.*)/?'),
    (handlers.boop, r'boopv?'),
    (handlers.timer, r'timer (\d+)'),
    (handlers.highlight_own, r'code([\w\W]+)'),
    (handlers.highlight_reply, r'high(\w+)?'),
]

nou_pattern = "|".join(NOU_LIST)
nou_pattern = '(' + nou_pattern + ')'
other_handlers = [
    (handlers.nou, nou_pattern),
]


def add_handlers(outgoing, other):
    for callback, pattern in outgoing:
        client.add_event_handler(callback, NewMessage(outgoing=True, pattern=pattern))
    for callback, pattern in other:
        client.add_event_handler(callback, NewMessage(pattern=pattern))


def remove_handlers(outgoing, other):
    for callback, _ in outgoing + other:
        client.remove_event_handler(callback)


add_handlers(outgoing_handlers, other_handlers)


@client.on(NewMessage(outgoing=True, pattern='toggle userbot'))
async def toggle(event):
    if STATUS['up']:
        remove_handlers(outgoing_handlers, other_handlers)
        message = f"🚨 Userbot '{USERBOT_NAME}' is down"
    else:
        add_handlers(outgoing_handlers, other_handlers)
        message = f"✅ Userbot '{USERBOT_NAME}' is up"
    STATUS['up'] = not STATUS['up']
    await event.respond(message)
    await event.delete()


if __name__ == '__main__':
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()
