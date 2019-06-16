import logging

from telethon import TelegramClient

import handlers
from argparse_extra import MergeAction
from manager import Manager, NewMessage
from persistence import load_session_file, set_save_before_term_hook
from config import (
    API_HASH,
    API_ID,
    USERBOT_NAME,
    USER_PASSWORD,
    USER_PHONE,
    configure_logging,
    NOU_LIST_REGEX,
    DEBUG,
)

configure_logging(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)


def setup_handlers(client: TelegramClient):
    m = Manager(client)

    m.add_handler(handlers.handle_help, NewMessage(cmd='', outgoing=True, parser=m.parser))
    m.add_handler(handlers.handle_nou, NewMessage(pattern=NOU_LIST_REGEX))

    with m.add_command('hello', "say hello from userbot", handlers.handle_hello):
        pass

    with m.add_command('e', "evaluate expression", handlers.handle_eval) as p:
        p.add_argument('expression', action=MergeAction)

    with m.add_command('s', "sed substitution (aka find and replace)", handlers.handle_sub) as p:
        p.add_argument('text', help='sed substitution string')
        p.add_argument('-h', dest='highlight', action='store_true', help="highlight replaced")

    with m.add_command('t', "timer", handlers.handle_timer) as p:
        p.add_argument('time', help='time is seconds')
        p.add_argument('-m', dest='message', help='message to show after time is up')

    with m.add_command('g', "google search", handlers.google) as p:
        p.add_argument('query', help='query to search', action=MergeAction)
        p.add_argument('-i', dest='image', action='store_true', help='image search')
        p.add_argument('-l', dest='let_me', action='store_true', help='"let me google for you"')

    with m.add_command('m', "magic moon loop", handlers.magic) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')
        p.add_argument('-w', dest='wide', action='store_true', help='use wide text')

    with m.add_command('mar', "marquee loop", handlers.marquee) as p:
        p.add_argument('text', action=MergeAction)
        p.add_argument('-c', dest='count', type=int, default=3, help='number of loops')

    with m.add_command('h', "highlight text/code block", handlers.highlight_code) as p:
        p.add_argument('text', nargs='*', action=MergeAction)
        p.add_argument('-l', dest='lang', help="programming language")
        p.add_argument('-c', dest='carbon', action='store_true', help="add carbon link")
        p.add_argument('--ln', dest='line_numbers', action='store_true', help="show line numbers")
        p.add_argument('-t', dest='theme', default='monokai', help="highlight theme")

    with m.add_command('r', "rotate image in reply", handlers.handle_rotate) as p:
        p.add_argument('angle', type=int, default=90, help="rotation angle")

    with m.add_command('loop_desc', "loop description", handlers.loop_description) as p:
        p.add_argument('-t', dest='type', help="type of description")
        p.add_argument('-s', dest='sleep', type=int, default=30, help='sleep/update interval')

    with m.add_command('loop_name', "loop name", handlers.loop_name) as p:
        p.add_argument('-s', dest='sleep', type=int, default=120, help='sleep/update interval')

    with m.add_command('logs', "show bot logs", handlers.handle_logs) as p:
        p.add_argument('-s', dest='size', type=int, default=20, help='number of lines to return')

    m.register_handlers()


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
