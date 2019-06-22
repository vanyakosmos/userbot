import atexit
import glob
import logging
import os
import re
from pprint import pformat
from typing import Optional

import redis
from telethon import TelegramClient
from asyncio import AbstractEventLoop
from config import API_ID, API_HASH, REDIS_URL
from manager import setup_handlers

logger = logging.getLogger(__name__)


async def try_connect(client):
    if not client.is_connected():
        await client.connect()


class Registry:
    sessions_dir = 'sessions'
    sessions_redis_key = 'TG_SESSIONS'

    def __init__(self):
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.store = {}

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

    def save_sessions_to_redis(self):
        if not REDIS_URL:
            logger.warning(f"Sessions are not saved, REDIS_URL not found.")
            return
        client = redis.from_url(REDIS_URL)
        for phone in self.store:
            s = self.get_session(phone)
            with open(f'{s}.session', 'rb') as f:
                session = f.read()
            client.hset(self.sessions_redis_key, phone, session)
        logger.debug(f"Sessions saved to redis: {list(self.store.keys())}")

    def load_sessions_from_redis(self):
        if not REDIS_URL:
            logger.warning(f"Sessions are not loaded, REDIS_URL not found.")
            return
        client = redis.from_url(REDIS_URL)
        sessions = client.hgetall(self.sessions_redis_key)
        for key, value in sessions.items():
            s = self.get_session(key.decode())
            with open(f'{s}.session', 'wb') as f:
                f.write(value)
        logger.debug(f"Sessions loaded from redis for {list(sessions.keys())}")

    def load_sessions_from_files(self, loop: AbstractEventLoop):
        for s in glob.glob(os.path.join(self.sessions_dir, '*.session')):
            s = os.path.split(s)[1]
            phone = re.match(r'^(.+)\.session$', s)[1]
            client = loop.run_until_complete(self.make_client(phone, loop=loop))
            registry.save_client(phone, client)

    def load_sessions(self, loop: AbstractEventLoop):
        atexit.register(self.save_sessions_to_redis)
        self.load_sessions_from_redis()
        self.load_sessions_from_files(loop)
        logger.info(f"Loaded sessions: {pformat(list(self.store.keys()))}")

    def save_client(self, phone: str, client: TelegramClient):
        self.store[phone] = client

    def get_client(self, phone: str) -> Optional[TelegramClient]:
        return self.store.get(phone)


registry = Registry()
