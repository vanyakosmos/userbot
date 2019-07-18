import argparse
import atexit
import json
import logging
from functools import wraps

import redis
from telethon import TelegramClient

from config import (
    API_HASH,
    API_ID,
    REDIS_URL,
    USERBOT_NAME,
    USER_PASSWORD,
    USER_PHONE,
    configure_logging,
)

logger = logging.getLogger(__name__)
SESSION_KEY = 'session'
redis_client = redis.Redis.from_url(REDIS_URL) if REDIS_URL else None


def with_redis_client(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if not redis_client:
            logger.warning(f"{f.__name__}: redis client is not created")
            return
        return f(*args, **kwargs)

    return dec


def create_session_file():
    client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    save_session_file()


@with_redis_client
def save_session_file():
    with open(USERBOT_NAME + '.session', 'rb') as f:
        session = f.read()
    redis_client.set(SESSION_KEY, session)
    logger.info(f"Session saved to redis under {SESSION_KEY} key.")


@with_redis_client
def load_session_file():
    session = redis_client.get(SESSION_KEY)
    if not session:
        logger.error('No session file to load.')
        return
    with open(USERBOT_NAME + '.session', 'wb') as f:
        f.write(session)
    logger.info(f"Session loaded from redis with {SESSION_KEY} key.")


def set_save_before_term_hook():
    atexit.register(save_session_file)


@with_redis_client
def save_json(key: str, value):
    redis_client.set(key, json.dumps(value))


@with_redis_client
def load_json(key: str):
    data = redis_client.get(key)
    return json.loads(data) if data else None


def main():
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['create', 'load'])
    args = parser.parse_args()
    if args.command == 'create':
        create_session_file()
    elif args.command == 'load':
        load_session_file()


if __name__ == '__main__':
    main()
