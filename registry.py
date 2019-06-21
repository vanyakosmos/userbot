import glob
import logging
import os
import re
from pprint import pformat
from typing import Optional

from telethon import TelegramClient
from asyncio import AbstractEventLoop
from config import API_ID, API_HASH
from manager import setup_handlers

logger = logging.getLogger(__name__)


async def try_connect(client):
    if not client.is_connected():
        await client.connect()


class Registry:
    sessions_dir = 'sessions'

    def __init__(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.store = {}

    def __str__(self):
        return pformat(self.store)

    def __contains__(self, item):
        if isinstance(item, TelegramClient):
            return item in self.store.values()
        return item in self.store

    @classmethod
    def get_session(cls, phone):
        return os.path.join(cls.sessions_dir, phone)

    @classmethod
    async def make_client(cls, phone, **kwargs):
        session = cls.get_session(phone)
        client = TelegramClient(session, API_ID, API_HASH, **kwargs)
        client.parse_mode = 'md'
        setup_handlers(client)
        await try_connect(client)
        return client

    def load_sessions(self, loop: AbstractEventLoop):
        for s in glob.glob(os.path.join(self.sessions_dir, '*.session')):
            s = os.path.split(s)[1]
            phone = re.match(r'^(.+)\.session$', s)[1]
            client = loop.run_until_complete(self.make_client(phone, loop=loop))
            registry.save_client(phone, client)
        logger.info(f"loaded sessions: {pformat(list(self.store.keys()))}")

    def save_client(self, phone: str, client: TelegramClient):
        self.store[phone] = client

    def get_client(self, phone: str) -> Optional[TelegramClient]:
        return self.store.get(phone)


registry = Registry()
