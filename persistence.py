import argparse
import atexit
import sys

import redis
from telethon import TelegramClient

from settings import API_HASH, API_ID, REDIS_URL, USERBOT_NAME, USER_PASSWORD, USER_PHONE


SESSION_KEY = 'session'


def create_session_file():
    client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    save_session_file()


def save_session_file():
    if not REDIS_URL:
        print(f"Session not saved.")
        return
    with open(USERBOT_NAME + '.session', 'rb') as f:
        session = f.read()
    client = redis.Redis.from_url(REDIS_URL)
    client.set(SESSION_KEY, session)
    print(f"Session saved to redis under {SESSION_KEY} key.")


def load_session_file():
    if not REDIS_URL:
        print(f"Session not loaded.")
        return
    client = redis.Redis.from_url(REDIS_URL)
    session = client.get(SESSION_KEY)
    if not session:
        print('No session file to load.', file=sys.stderr)
        exit(1)
    with open(USERBOT_NAME + '.session', 'wb') as f:
        f.write(session)
    print(f"Session loaded from redis with {SESSION_KEY} key.")


def save_before_term():
    atexit.register(save_session_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['create', 'load'])
    args = parser.parse_args()
    if args.command == 'create':
        create_session_file()
    elif args.command == 'load':
        load_session_file()


if __name__ == '__main__':
    main()
