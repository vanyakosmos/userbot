"""
Run single client.
"""
import logging

from telethon import TelegramClient

from config import (
    API_HASH,
    API_ID,
    DEBUG,
    USERBOT_NAME,
    USER_PASSWORD,
    USER_PHONE,
    configure_logging,
)
from manager import setup_handlers
from persistence import load_session_file, set_save_before_term_hook

configure_logging(level=DEBUG and logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    set_save_before_term_hook()
    load_session_file()

    client = TelegramClient(USERBOT_NAME, API_ID, API_HASH)
    client.parse_mode = 'md'

    logger.info("setting up...")
    setup_handlers(client)

    logger.info("starting...")
    client.start(phone=USER_PHONE, password=USER_PASSWORD)
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
