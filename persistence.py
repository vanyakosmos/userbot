import argparse
import atexit
import logging

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


def create_session_file():
    client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    save_session_file()


def save_session_file():
    if not REDIS_URL:
        logger.warning(f"Session is not saved, REDIS_URL not found.")
        return
    with open(USERBOT_NAME + '.session', 'rb') as f:
        session = f.read()
    client = redis.Redis.from_url(REDIS_URL)
    client.set(SESSION_KEY, session)
    logger.info(f"Session saved to redis under {SESSION_KEY} key.")


def load_session_file():
    if not REDIS_URL:
        logger.warning(f"Session not loaded, REDIS_URL not found.")
        return
    client = redis.Redis.from_url(REDIS_URL)
    session = client.get(SESSION_KEY)
    if not session:
        logger.error('No session file to load.')
        exit(1)
    with open(USERBOT_NAME + '.session', 'wb') as f:
        f.write(session)
    logger.info(f"Session loaded from redis with {SESSION_KEY} key.")


def set_save_before_term_hook():
    atexit.register(save_session_file)


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
